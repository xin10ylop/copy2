//! Our buy and sell transactions: legacy when they fit (a 2-hop route with
//! the wrap, the ATA, the budget and the tip does), else v0 with pump's own
//! lookup table (a 3-hop route: about 1,270 bytes legacy, 1,027 v0;
//! `analysis/research/2026-10-28/more/` §B).
//!
//! * **Buy**: compute budget; when paying wrapped SOL, create our wSOL ATA,
//!   transfer the stake in, `SyncNative`; create the coin ATA;
//!   `multi_hop_swap`; close the wSOL ATA (the wallet stays in native SOL);
//!   the tip.
//! * **Sell**: compute budget; the wSOL ATA when ending in wrapped SOL;
//!   `multi_hop_swap` of every token we hold back along the route; close
//!   the wSOL ATA and the emptied coin ATA (its rent comes back); the tip.

use pump_codec::constants as c;
use pump_codec::instructions as pi;
use pump_codec::multihop::{self, MultiHop, Route};
use pump_codec::{pda, Instruction, Pubkey};
use rugsnipe_tx::msg::{compile_signed_legacy, compile_signed_v0, CompileError, LookupTable};
use std::sync::OnceLock;

/// pump's mainnet lookup table (`PUMP_MAINNET_ALT`), read from the chain at
/// start ([`set_lookup_table`]): a transaction too big for legacy is sent
/// as v0 with it.
static PUMP_ALT: OnceLock<LookupTable> = OnceLock::new();

/// The addresses of a lookup table account (they start after its 56-byte
/// header).
pub fn parse_lookup_table(key: Pubkey, data: &[u8]) -> Option<LookupTable> {
    let body = data.get(56..)?;
    (body.len() % 32 == 0 && !body.is_empty()).then(|| LookupTable {
        key,
        addresses: body
            .chunks_exact(32)
            .map(|c| Pubkey::new_from_array(c.try_into().expect("32 bytes")))
            .collect(),
    })
}

/// Set pump's lookup table once (later calls are ignored).
pub fn set_lookup_table(t: LookupTable) {
    let _ = PUMP_ALT.set(t);
}

pub fn lookup_table() -> Option<&'static LookupTable> {
    PUMP_ALT.get()
}

/// Budget and tip of one transaction.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Fees {
    pub cu_limit: u32,
    /// Micro-lamports per compute unit.
    pub cu_price: u64,
    /// Tip account and lamports (`None`: no tip, e.g. plain RPC).
    pub tip: Option<(Pubkey, u64)>,
}

fn budget(f: &Fees) -> Vec<Instruction> {
    vec![
        pi::set_compute_unit_limit(f.cu_limit),
        pi::set_compute_unit_price(f.cu_price),
    ]
}

fn tip(user: &Pubkey, f: &Fees) -> Option<Instruction> {
    f.tip
        .filter(|(_, l)| *l > 0)
        .map(|(to, l)| pi::system_transfer(user, &to, l))
}

/// The buy: `amount_in` of `route.input` (lamports when wrapped SOL) for at
/// least `min_out` coin tokens.
pub fn buy_ixs(
    user: &Pubkey,
    route: &Route,
    anchor_program: &Pubkey,
    coin_program: &Pubkey,
    amount_in: u64,
    min_out: u64,
    fees: &Fees,
    buyback_index: usize,
) -> Vec<Instruction> {
    let anchor = route.input;
    let coin = route.output();
    let anchor_ata = pda::associated_token_address(user, &anchor, anchor_program);
    let coin_ata = pda::associated_token_address(user, &coin, coin_program);
    let wsol = anchor == c::WSOL_MINT;
    let mut v = budget(fees);
    if wsol {
        v.push(pi::create_associated_token_account_idempotent(
            user,
            user,
            &c::WSOL_MINT,
            &c::SPL_TOKEN_PROGRAM_ID,
        ));
        v.push(pi::system_transfer(user, &anchor_ata, amount_in));
        v.push(pi::spl_sync_native(&anchor_ata));
    }
    v.push(pi::create_associated_token_account_idempotent(
        user,
        user,
        &coin,
        coin_program,
    ));
    v.push(multihop::multi_hop_swap(&MultiHop {
        user: *user,
        user_in: anchor_ata,
        user_out: coin_ata,
        route,
        outer_mint: anchor,
        outer_token_program: *anchor_program,
        buyback_index,
        amount_in,
        min_amount_out: min_out,
    }));
    if wsol {
        v.push(pi::spl_close_account(&anchor_ata, user, user));
    }
    v.extend(tip(user, fees));
    v
}

/// The sell: `tokens` coin tokens back along `route` (the buy route
/// reversed: coin first) for at least `min_out` of the anchor. With
/// `close_coin`, the coin ATA is closed after (sell every token we hold).
pub fn sell_ixs(
    user: &Pubkey,
    route: &Route,
    anchor_program: &Pubkey,
    coin_program: &Pubkey,
    tokens: u64,
    min_out: u64,
    close_coin: bool,
    fees: &Fees,
    buyback_index: usize,
) -> Vec<Instruction> {
    let coin = route.input;
    let anchor = route.output();
    let anchor_ata = pda::associated_token_address(user, &anchor, anchor_program);
    let coin_ata = pda::associated_token_address(user, &coin, coin_program);
    let wsol = anchor == c::WSOL_MINT;
    let mut v = budget(fees);
    // the account the proceeds land in: wrapped SOL's is created here and
    // closed after; a float's exists while we hold the float, but is
    // created all the same (idempotent) so that a sell never fails on a
    // closed account (2026-10-28, simulated: `AccountNotInitialized`)
    v.push(pi::create_associated_token_account_idempotent(
        user,
        user,
        &anchor,
        anchor_program,
    ));
    v.push(multihop::multi_hop_swap(&MultiHop {
        user: *user,
        user_in: coin_ata,
        user_out: anchor_ata,
        route,
        outer_mint: anchor,
        outer_token_program: *anchor_program,
        buyback_index,
        amount_in: tokens,
        min_amount_out: min_out,
    }));
    if wsol {
        v.push(pi::spl_close_account(&anchor_ata, user, user));
    }
    if close_coin {
        v.push(pi::token_close_account(coin_program, &coin_ata, user, user));
    }
    v.extend(tip(user, fees));
    v
}

/// Compile and sign: legacy, or v0 with pump's lookup table when legacy is
/// too long (a 3-hop route). `sign` signs the message bytes.
pub fn sign(
    user: &Pubkey,
    ixs: &[Instruction],
    blockhash: &[u8; 32],
    sign: impl Fn(&[u8]) -> [u8; 64],
) -> Result<(Vec<u8>, [u8; 64]), CompileError> {
    sign_with(user, ixs, blockhash, lookup_table(), sign)
}

/// [`sign`] with an explicit table (tests).
pub fn sign_with(
    user: &Pubkey,
    ixs: &[Instruction],
    blockhash: &[u8; 32],
    table: Option<&LookupTable>,
    sign: impl Fn(&[u8]) -> [u8; 64],
) -> Result<(Vec<u8>, [u8; 64]), CompileError> {
    match compile_signed_legacy(user, ixs, blockhash, &sign) {
        Err(CompileError::TooLong(n)) => match table {
            Some(t) => compile_signed_v0(user, ixs, blockhash, t, &sign),
            None => Err(CompileError::TooLong(n)),
        },
        r => r,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pump_codec::multihop::Hop;

    fn k(n: u8) -> Pubkey {
        Pubkey::new_from_array([n; 32])
    }

    fn two_hops_from_wsol() -> Route {
        let (q, coin) = (k(5), k(7));
        let pool = Hop::pool(
            &k(9),
            &q,
            &c::TOKEN_2022_PROGRAM_ID,
            &c::WSOL_MINT,
            &c::SPL_TOKEN_PROGRAM_ID,
        );
        let curve = Hop::curve(
            &coin,
            &c::TOKEN_2022_PROGRAM_ID,
            &q,
            &c::TOKEN_2022_PROGRAM_ID,
        );
        Route::new(c::WSOL_MINT, vec![pool, curve]).unwrap()
    }

    #[test]
    fn a_two_hop_buy_and_sell_from_wsol_fit_one_transaction() {
        let user = k(1);
        let r = two_hops_from_wsol();
        let fees = Fees {
            cu_limit: 300_000,
            cu_price: 2_000_000,
            tip: Some((k(2), 1_000_000)),
        };
        let b = buy_ixs(
            &user,
            &r,
            &c::SPL_TOKEN_PROGRAM_ID,
            &c::TOKEN_2022_PROGRAM_ID,
            1_000_000_000,
            1,
            &fees,
            0,
        );
        let (bytes, _) = sign(&user, &b, &[0; 32], |_| [7; 64]).unwrap();
        assert!(bytes.len() <= rugsnipe_tx::MAX_TX_LEN, "{}", bytes.len());
        let s = sell_ixs(
            &user,
            &r.reversed(),
            &c::SPL_TOKEN_PROGRAM_ID,
            &c::TOKEN_2022_PROGRAM_ID,
            5,
            1,
            true,
            &fees,
            0,
        );
        let (bytes, sig) = sign(&user, &s, &[0; 32], |_| [7; 64]).unwrap();
        assert!(bytes.len() <= rugsnipe_tx::MAX_TX_LEN, "{}", bytes.len());
        assert_eq!(sig, [7; 64]);
        assert_eq!(&bytes[1..65], &[7; 64]);
    }

    #[test]
    fn a_three_hop_buy_and_sell_go_as_v0_with_pumps_table_and_fit() {
        use pump_codec::tx::{TxVersion, TxView};
        // pump's mainnet lookup table as read from the chain on 2026-11-13 (184 addresses)
        let table = parse_lookup_table(
            c::PUMP_MAINNET_ALT,
            include_bytes!("../tests/fixtures/pump_alt.bin"),
        )
        .unwrap();
        assert_eq!(table.addresses.len(), 184);
        let user = k(1);
        let (q1, q2, coin) = (k(4), k(5), k(7));
        let r = Route::new(
            c::WSOL_MINT,
            vec![
                Hop::pool(
                    &k(9),
                    &q1,
                    &c::SPL_TOKEN_PROGRAM_ID,
                    &c::WSOL_MINT,
                    &c::SPL_TOKEN_PROGRAM_ID,
                ),
                Hop::pool(
                    &k(8),
                    &q2,
                    &c::TOKEN_2022_PROGRAM_ID,
                    &q1,
                    &c::SPL_TOKEN_PROGRAM_ID,
                ),
                Hop::curve(
                    &coin,
                    &c::TOKEN_2022_PROGRAM_ID,
                    &q2,
                    &c::TOKEN_2022_PROGRAM_ID,
                ),
            ],
        )
        .unwrap();
        let fees = Fees {
            cu_limit: 400_000,
            cu_price: 2_000_000,
            tip: Some((k(2), 1_000_000)),
        };
        let b = buy_ixs(
            &user,
            &r,
            &c::SPL_TOKEN_PROGRAM_ID,
            &c::TOKEN_2022_PROGRAM_ID,
            500_000_000,
            1,
            &fees,
            0,
        );
        let s = sell_ixs(
            &user,
            &r.reversed(),
            &c::SPL_TOKEN_PROGRAM_ID,
            &c::TOKEN_2022_PROGRAM_ID,
            5,
            1,
            true,
            &fees,
            0,
        );
        for ixs in [&b, &s] {
            // too long for legacy: refused without the table
            assert!(matches!(
                sign_with(&user, ixs, &[0; 32], None, |_| [7; 64]),
                Err(CompileError::TooLong(_))
            ));
            let (bytes, sig) = sign_with(&user, ixs, &[0; 32], Some(&table), |_| [7; 64]).unwrap();
            assert!(bytes.len() <= rugsnipe_tx::MAX_TX_LEN, "{}", bytes.len());
            assert_eq!(sig, [7; 64]);
            let v = TxView::parse(&bytes).unwrap();
            assert_eq!(v.version(), TxVersion::V0);
            assert_eq!(v.fee_payer(), &user);
            assert_eq!(v.num_instructions(), ixs.len());
            let (w, ro) = v.num_lookup_accounts();
            assert!(
                w + ro >= 8,
                "pump's fixed accounts come from the table: {w} + {ro}"
            );
        }
        // a 2-hop buy stays legacy with the table set
        let b2 = buy_ixs(
            &user,
            &two_hops_from_wsol(),
            &c::SPL_TOKEN_PROGRAM_ID,
            &c::TOKEN_2022_PROGRAM_ID,
            1,
            1,
            &fees,
            0,
        );
        let (bytes, _) = sign_with(&user, &b2, &[0; 32], Some(&table), |_| [7; 64]).unwrap();
        assert_eq!(TxView::parse(&bytes).unwrap().version(), TxVersion::Legacy);
    }

    #[test]
    fn the_buy_wraps_exactly_the_stake_and_unwraps_after() {
        let user = k(1);
        let r = two_hops_from_wsol();
        let fees = Fees {
            cu_limit: 1,
            cu_price: 1,
            tip: None,
        };
        let b = buy_ixs(
            &user,
            &r,
            &c::SPL_TOKEN_PROGRAM_ID,
            &c::TOKEN_2022_PROGRAM_ID,
            123,
            4,
            &fees,
            3,
        );
        assert_eq!(b.len(), 2 + 3 + 1 + 1 + 1);
        let wsol_ata =
            pda::associated_token_address(&user, &c::WSOL_MINT, &c::SPL_TOKEN_PROGRAM_ID);
        assert_eq!(b[3].accounts[1].pubkey, wsol_ata);
        assert_eq!(&b[3].data[4..12], &123u64.to_le_bytes());
        let mh = &b[6];
        assert_eq!(mh.program_id, c::PUMP_SWAP_PROGRAM_ID);
        assert_eq!(mh.accounts[1].pubkey, wsol_ata);
        assert_eq!(
            mh.accounts[6].pubkey,
            multihop::buyback_fee_account(3, &c::WSOL_MINT, &c::SPL_TOKEN_PROGRAM_ID)
        );
        assert_eq!(b[7].program_id, c::SPL_TOKEN_PROGRAM_ID);
        assert_eq!(b[7].data, vec![9]);
    }
}
