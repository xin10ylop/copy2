//! Fixed-order message compiler.
//!
//! The caller fixes the order of every account key (Solana only requires the
//! four classes signer-writable, signer-readonly, writable, readonly in that
//! order; inside a class the order is free). Fixed positions are what make
//! the [`crate::template::PatchTable`] possible: a mint-dependent key always
//! sits at the same byte offset, so a new mint is a few `memcpy`s.
//!
//! Layouts written:
//! * legacy: `compact(n_sigs) | sigs | header(3) | compact(n_keys) | keys |
//!   blockhash | compact(n_ix) | (prog u8 | compact(n) | idx | compact(len) | data)*`;
//! * v1 (SIMD-0385): `0x81 | header(3) | mask u32 | lifetime | n_ix u8 |
//!   n_addr u8 | keys | config values | (prog u8, n_acc u8, len u16)* |
//!   (idx | data)* | sigs` (signatures at the tail).

use pump_codec::{AccountMeta, Instruction, Pubkey};

/// v1 transaction config (mask bits 0-3).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct V1Config {
    /// Bits 0+1: total priority fee in lamports.
    pub priority_fee_lamports: u64,
    /// Bit 2 (unset = 0 = the transaction fails and still pays).
    pub compute_unit_limit: u32,
    /// Bit 3 (unset = 0 = fails on load).
    pub loaded_accounts_data_size_limit: u32,
}

/// Which format to write.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Format {
    Legacy,
    V1(V1Config),
}

/// One ordered key with its class.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct KeySpec {
    pub key: Pubkey,
    pub signer: bool,
    pub writable: bool,
}

impl KeySpec {
    pub const fn new(key: Pubkey, signer: bool, writable: bool) -> Self {
        Self {
            key,
            signer,
            writable,
        }
    }
}

/// Where things landed in the serialized transaction.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Layout {
    /// Offset of key `i` (32 bytes each).
    pub key_offsets: Vec<usize>,
    /// Offset of the blockhash / lifetime.
    pub lifetime: usize,
    /// Offset of each instruction's data.
    pub ix_data: Vec<usize>,
    /// v1: offset of the u64 priority fee in the config values.
    pub v1_priority: Option<usize>,
    /// v1: offsets of the u32 CU limit and LADS values.
    pub v1_cu_limit: Option<usize>,
    pub v1_lads: Option<usize>,
    /// First signature byte (64 bytes per signer, in key order).
    pub sigs: usize,
    pub n_sigs: usize,
    /// Signed message range `[start, end)`.
    pub message: (usize, usize),
}

/// Compile error.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CompileError {
    /// Keys are not in signer-w, signer-ro, w, ro class order.
    ClassOrder(usize),
    DuplicateKey(Pubkey),
    /// An instruction uses a key that is not in the list.
    MissingKey(Pubkey),
    /// An instruction needs a flag (signer / writable) the key's class lacks.
    FlagMismatch(Pubkey),
    TooMany(&'static str),
    TooLong(usize),
}

impl core::fmt::Display for CompileError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(f, "{self:?}")
    }
}
impl std::error::Error for CompileError {}

fn class(k: &KeySpec) -> u8 {
    match (k.signer, k.writable) {
        (true, true) => 0,
        (true, false) => 1,
        (false, true) => 2,
        (false, false) => 3,
    }
}

fn compact_u16(out: &mut Vec<u8>, mut v: usize) {
    loop {
        let mut b = (v & 0x7f) as u8;
        v >>= 7;
        if v != 0 {
            b |= 0x80;
        }
        out.push(b);
        if v == 0 {
            break;
        }
    }
}

/// The key order for `ixs` paid by `payer`, for a transaction whose layout
/// nothing patches (the cold paths, `rugsnipe-long`): the payer first, then
/// every other key in first-use order within its class (signer-writable,
/// signer-readonly, writable, readonly), each with the union of the flags
/// its instructions ask for. Program ids are read-only.
pub fn keys_for(payer: &Pubkey, ixs: &[Instruction]) -> Vec<KeySpec> {
    let mut v = vec![KeySpec::new(*payer, true, true)];
    let mut add = |k: Pubkey, s: bool, w: bool| match v.iter_mut().find(|e| e.key == k) {
        Some(e) => {
            e.signer |= s;
            e.writable |= w;
        }
        None => v.push(KeySpec::new(k, s, w)),
    };
    for ix in ixs {
        for m in &ix.accounts {
            add(m.pubkey, m.is_signer, m.is_writable);
        }
        add(ix.program_id, false, false);
    }
    let mut rest = v.split_off(1);
    rest.sort_by_key(class);
    v[0].signer = true;
    v[0].writable = true;
    v.extend(rest);
    v
}

/// [`keys_for`] + [`compile`] into a legacy transaction, signed by `sign`
/// (the payer's signature over the message; the payer must be the only
/// signer). Returns the bytes and the signature.
pub fn compile_signed_legacy(
    payer: &Pubkey,
    ixs: &[Instruction],
    blockhash: &[u8; 32],
    sign: impl FnOnce(&[u8]) -> [u8; 64],
) -> Result<(Vec<u8>, [u8; 64]), CompileError> {
    let keys = keys_for(payer, ixs);
    let (mut bytes, layout) = compile(&keys, ixs, blockhash, Format::Legacy)?;
    if layout.n_sigs != 1 {
        return Err(CompileError::TooMany("signers (the payer must sign alone)"));
    }
    let sig = sign(&bytes[layout.message.0..layout.message.1]);
    bytes[layout.sigs..layout.sigs + 64].copy_from_slice(&sig);
    Ok((bytes, sig))
}

/// An address lookup table: its account and the addresses it holds, in
/// order (an address's index in the table is its position here).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LookupTable {
    pub key: Pubkey,
    pub addresses: Vec<Pubkey>,
}

/// [`keys_for`] compiled into a v0 transaction that loads from `table`
/// every key it holds that is neither a signer nor a program id (the
/// runtime only invokes static keys), signed by `sign` (the payer alone).
/// Layout: `compact(n_sigs) | sigs | 0x80 | header(3) | compact(n_static) |
/// static keys | blockhash | compact(n_ix) | (prog u8 | compact(n) | idx* |
/// compact(len) | data)* | compact(1) | table | compact(n_w) | w idx* |
/// compact(n_r) | r idx*`; account indexes run over the static keys, then
/// the loaded writable, then the loaded read-only ones.
pub fn compile_signed_v0(
    payer: &Pubkey,
    ixs: &[Instruction],
    blockhash: &[u8; 32],
    table: &LookupTable,
    sign: impl FnOnce(&[u8]) -> [u8; 64],
) -> Result<(Vec<u8>, [u8; 64]), CompileError> {
    let keys = keys_for(payer, ixs);
    let programs: Vec<Pubkey> = ixs.iter().map(|ix| ix.program_id).collect();
    let in_table = |k: &Pubkey| table.addresses.iter().position(|a| a == k);
    let loadable =
        |k: &KeySpec| !k.signer && !programs.contains(&k.key) && in_table(&k.key).is_some();
    let stat: Vec<KeySpec> = keys.iter().filter(|k| !loadable(k)).copied().collect();
    let lw: Vec<KeySpec> = keys
        .iter()
        .filter(|k| loadable(k) && k.writable)
        .copied()
        .collect();
    let lr: Vec<KeySpec> = keys
        .iter()
        .filter(|k| loadable(k) && !k.writable)
        .copied()
        .collect();
    if stat.iter().filter(|k| k.signer).count() != 1 {
        return Err(CompileError::TooMany("signers (the payer must sign alone)"));
    }
    if keys.len() > 256 || table.addresses.len() > 256 || ixs.len() > 64 {
        return Err(CompileError::TooMany("keys/instructions"));
    }
    let all: Vec<Pubkey> = stat.iter().chain(&lw).chain(&lr).map(|k| k.key).collect();
    let idx = |k: &Pubkey| all.iter().position(|a| a == k);
    let n_ro_signed = stat.iter().filter(|k| k.signer && !k.writable).count();
    let n_ro_unsigned = stat.iter().filter(|k| !k.signer && !k.writable).count();
    let mut out = Vec::with_capacity(1_232);
    compact_u16(&mut out, 1);
    let sigs = out.len();
    out.resize(out.len() + 64, 0);
    let msg_start = out.len();
    out.push(0x80);
    out.extend_from_slice(&[1, n_ro_signed as u8, n_ro_unsigned as u8]);
    compact_u16(&mut out, stat.len());
    for k in &stat {
        out.extend_from_slice(k.key.as_ref());
    }
    out.extend_from_slice(blockhash);
    compact_u16(&mut out, ixs.len());
    for ix in ixs {
        let p = idx(&ix.program_id).ok_or(CompileError::MissingKey(ix.program_id))?;
        out.push(p as u8);
        compact_u16(&mut out, ix.accounts.len());
        for m in &ix.accounts {
            out.push(idx(&m.pubkey).ok_or(CompileError::MissingKey(m.pubkey))? as u8);
        }
        compact_u16(&mut out, ix.data.len());
        out.extend_from_slice(&ix.data);
    }
    compact_u16(&mut out, 1);
    out.extend_from_slice(table.key.as_ref());
    for part in [&lw, &lr] {
        compact_u16(&mut out, part.len());
        for k in part.iter() {
            out.push(in_table(&k.key).expect("loadable keys are in the table") as u8);
        }
    }
    if out.len() > crate::MAX_TX_LEN {
        return Err(CompileError::TooLong(out.len()));
    }
    let sig = sign(&out[msg_start..]);
    out[sigs..sigs + 64].copy_from_slice(&sig);
    Ok((out, sig))
}

/// Compile `ixs` over the exact key order `keys` into a zero-signed
/// transaction. Every instruction account must exist in `keys` with at
/// least the flags the instruction asks for; extra flags are an error
/// unless another instruction needs them (no silent privilege escalation).
pub fn compile(
    keys: &[KeySpec],
    ixs: &[Instruction],
    lifetime: &[u8; 32],
    format: Format,
) -> Result<(Vec<u8>, Layout), CompileError> {
    // class order + duplicates
    for i in 1..keys.len() {
        if class(&keys[i]) < class(&keys[i - 1]) {
            return Err(CompileError::ClassOrder(i));
        }
    }
    for (i, k) in keys.iter().enumerate() {
        if keys[..i].iter().any(|o| o.key == k.key) {
            return Err(CompileError::DuplicateKey(k.key));
        }
    }
    let idx = |k: &Pubkey| keys.iter().position(|s| s.key == *k);
    // flags: needed (union over instructions) must equal the class flags
    let mut need = vec![(false, false); keys.len()];
    let mut used = vec![false; keys.len()];
    let mut compiled: Vec<(u8, Vec<u8>, &[u8])> = Vec::with_capacity(ixs.len());
    for ix in ixs {
        let p = idx(&ix.program_id).ok_or(CompileError::MissingKey(ix.program_id))?;
        used[p] = true;
        let mut accts = Vec::with_capacity(ix.accounts.len());
        for AccountMeta {
            pubkey,
            is_signer,
            is_writable,
        } in &ix.accounts
        {
            let i = idx(pubkey).ok_or(CompileError::MissingKey(*pubkey))?;
            used[i] = true;
            need[i].0 |= *is_signer;
            need[i].1 |= *is_writable;
            accts.push(i as u8);
        }
        compiled.push((p as u8, accts, &ix.data));
    }
    for (i, k) in keys.iter().enumerate() {
        // The fee payer (key 0) is always a writable signer.
        let (s, w) = if i == 0 { (true, true) } else { need[i] };
        if (s, w) != (k.signer, k.writable) || !(used[i] || i == 0) {
            return Err(CompileError::FlagMismatch(k.key));
        }
    }
    let n_sig = keys.iter().filter(|k| k.signer).count();
    let n_ro_signed = keys.iter().filter(|k| k.signer && !k.writable).count();
    let n_ro_unsigned = keys.iter().filter(|k| !k.signer && !k.writable).count();
    if keys.len() > 64 || ixs.len() > 64 {
        return Err(CompileError::TooMany("keys/instructions (v1 limit 64)"));
    }
    let header = [n_sig as u8, n_ro_signed as u8, n_ro_unsigned as u8];
    let mut out = Vec::with_capacity(1_232);
    let mut key_offsets = Vec::with_capacity(keys.len());
    let mut ix_data = Vec::with_capacity(ixs.len());
    let layout = match format {
        Format::Legacy => {
            compact_u16(&mut out, n_sig);
            let sigs = out.len();
            out.resize(out.len() + 64 * n_sig, 0);
            let msg_start = out.len();
            out.extend_from_slice(&header);
            compact_u16(&mut out, keys.len());
            for k in keys {
                key_offsets.push(out.len());
                out.extend_from_slice(k.key.as_ref());
            }
            let lt = out.len();
            out.extend_from_slice(lifetime);
            compact_u16(&mut out, compiled.len());
            for (p, a, d) in &compiled {
                out.push(*p);
                compact_u16(&mut out, a.len());
                out.extend_from_slice(a);
                compact_u16(&mut out, d.len());
                ix_data.push(out.len());
                out.extend_from_slice(d);
            }
            Layout {
                key_offsets,
                lifetime: lt,
                ix_data,
                v1_priority: None,
                v1_cu_limit: None,
                v1_lads: None,
                sigs,
                n_sigs: n_sig,
                message: (msg_start, out.len()),
            }
        }
        Format::V1(cfg) => {
            out.push(0x81);
            out.extend_from_slice(&header);
            out.extend_from_slice(&0x0Fu32.to_le_bytes());
            let lt = out.len();
            out.extend_from_slice(lifetime);
            out.push(compiled.len() as u8);
            out.push(keys.len() as u8);
            for k in keys {
                key_offsets.push(out.len());
                out.extend_from_slice(k.key.as_ref());
            }
            let pr = out.len();
            out.extend_from_slice(&cfg.priority_fee_lamports.to_le_bytes());
            let cu = out.len();
            out.extend_from_slice(&cfg.compute_unit_limit.to_le_bytes());
            let la = out.len();
            out.extend_from_slice(&cfg.loaded_accounts_data_size_limit.to_le_bytes());
            for (p, a, d) in &compiled {
                if a.len() > 255 || d.len() > u16::MAX as usize {
                    return Err(CompileError::TooMany("v1 instruction accounts/data"));
                }
                out.push(*p);
                out.push(a.len() as u8);
                out.extend_from_slice(&(d.len() as u16).to_le_bytes());
            }
            for (_, a, d) in &compiled {
                out.extend_from_slice(a);
                ix_data.push(out.len());
                out.extend_from_slice(d);
            }
            let msg_end = out.len();
            let sigs = out.len();
            out.resize(out.len() + 64 * n_sig, 0);
            Layout {
                key_offsets,
                lifetime: lt,
                ix_data,
                v1_priority: Some(pr),
                v1_cu_limit: Some(cu),
                v1_lads: Some(la),
                sigs,
                n_sigs: n_sig,
                message: (0, msg_end),
            }
        }
    };
    if out.len() > crate::MAX_TX_LEN {
        return Err(CompileError::TooLong(out.len()));
    }
    Ok((out, layout))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn a_v0_transaction_loads_from_the_table_and_decodes_to_the_same_instructions() {
        use pump_codec::instructions::AccountLookup;
        use pump_codec::tx::{TxVersion, TxView};
        let u = |n: u8| Pubkey::new_from_array([n; 32]);
        let (payer, prog_a, prog_b) = (u(1), u(2), u(3));
        // in the table: a program (must stay static), a writable and two read-only keys
        let table = LookupTable {
            key: u(99),
            addresses: vec![u(50), prog_b, u(10), u(11), u(12)],
        };
        let ixs = vec![
            Instruction {
                program_id: prog_a,
                accounts: vec![
                    AccountMeta::new(payer, true),
                    AccountMeta::new(u(10), false),
                    AccountMeta::new_readonly(u(11), false),
                    AccountMeta::new(u(20), false),
                ],
                data: vec![1, 2, 3],
            },
            Instruction {
                program_id: prog_b,
                accounts: vec![
                    AccountMeta::new_readonly(u(12), false),
                    AccountMeta::new_readonly(u(21), false),
                    AccountMeta::new(u(10), false),
                ],
                data: vec![9],
            },
        ];
        let (bytes, sig) = compile_signed_v0(&payer, &ixs, &[5; 32], &table, |m| {
            assert_eq!(m[0], 0x80, "the message starts with the v0 prefix");
            [7; 64]
        })
        .unwrap();
        assert_eq!(sig, [7; 64]);
        let v = TxView::parse(&bytes).unwrap();
        assert_eq!(v.version(), TxVersion::V0);
        assert_eq!(v.fee_payer(), &payer);
        assert_eq!(v.recent_blockhash(), &[5; 32]);
        assert_eq!(v.signature(0), Some(&[7; 64]));
        let lk: Vec<_> = v.address_table_lookups().collect();
        assert_eq!(lk.len(), 1);
        assert_eq!(lk[0].account_key, &u(99));
        // the runtime resolves writable indexes first, then read-only ones
        let loaded: Vec<Pubkey> = lk[0]
            .writable_indexes
            .iter()
            .chain(lk[0].readonly_indexes)
            .map(|i| table.addresses[*i as usize])
            .collect();
        assert_eq!(loaded, vec![u(10), u(11), u(12)]);
        assert!(!v.static_account_keys().contains(&u(10)));
        assert!(
            v.static_account_keys().contains(&prog_b),
            "programs stay static"
        );
        for (ix, view) in ixs.iter().zip(v.instructions()) {
            assert_eq!(v.program_id(&view), &ix.program_id);
            let acc = v.instruction_accounts(&view, Some(&loaded));
            assert_eq!(acc.account_count(), ix.accounts.len());
            for (i, m) in ix.accounts.iter().enumerate() {
                assert_eq!(acc.account(i), Some(m.pubkey));
                let t = acc.index(i).unwrap() as usize;
                assert_eq!(v.is_signer(t), m.is_signer, "{i}");
                assert!(v.is_writable(t) >= m.is_writable, "{i}");
            }
        }
    }

    #[test]
    fn compact_encoding() {
        for (v, want) in [
            (0usize, vec![0u8]),
            (127, vec![0x7f]),
            (128, vec![0x80, 1]),
            (16384, vec![0x80, 0x80, 1]),
        ] {
            let mut o = vec![];
            compact_u16(&mut o, v);
            assert_eq!(o, want);
        }
    }

    #[test]
    fn rejects_bad_orders_and_flags() {
        let (a, b, p) = (
            Pubkey::new_unique(),
            Pubkey::new_unique(),
            Pubkey::new_unique(),
        );
        let ix = Instruction {
            program_id: p,
            accounts: vec![AccountMeta::new(b, false)],
            data: vec![1],
        };
        let ok = [
            KeySpec::new(a, true, true),
            KeySpec::new(b, false, true),
            KeySpec::new(p, false, false),
        ];
        assert!(compile(&ok, std::slice::from_ref(&ix), &[0; 32], Format::Legacy).is_ok());
        let bad_order = [
            KeySpec::new(a, true, true),
            KeySpec::new(p, false, false),
            KeySpec::new(b, false, true),
        ];
        assert_eq!(
            compile(
                &bad_order,
                std::slice::from_ref(&ix),
                &[0; 32],
                Format::Legacy
            )
            .unwrap_err(),
            CompileError::ClassOrder(2)
        );
        let escalated = [
            KeySpec::new(a, true, true),
            KeySpec::new(b, true, true),
            KeySpec::new(p, false, false),
        ];
        assert_eq!(
            compile(
                &escalated,
                std::slice::from_ref(&ix),
                &[0; 32],
                Format::Legacy
            )
            .unwrap_err(),
            CompileError::FlagMismatch(b)
        );
        let missing = [KeySpec::new(a, true, true), KeySpec::new(p, false, false)];
        assert_eq!(
            compile(&missing, &[ix], &[0; 32], Format::Legacy).unwrap_err(),
            CompileError::MissingKey(b)
        );
    }
}
