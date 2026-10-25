use std::cmp::Ordering;
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Key(pub u32);
impl Ord for Key {
    fn cmp(&self, other: &Self) -> Ordering { self.0.cmp(&other.0) }
}
impl PartialOrd for Key {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> { Some(self.cmp(other)) }
}

/// Shared immutable data is intentionally part of this internal API.
pub fn snapshot() -> Arc<[u8]> { Arc::from([1, 2, 3]) }

/// The literal is controlled by this program, never external input.
pub fn invariant() -> u8 { "7".parse().expect("built-in literal is valid u8") }

/// Recovery discards potentially inconsistent state before exposing it.
pub fn reset_on_poison(state: &Mutex<Vec<u8>>) -> Vec<u8> {
    match state.lock() {
        Ok(guard) => guard.clone(),
        Err(poison) => {
            let mut guard = poison.into_inner();
            guard.clear();
            state.clear_poison();
            guard.clone()
        }
    }
}

/// Returns the first byte of externally supplied input.
pub fn first(input: &[u8]) -> u8 { input[0] }

/// Returns the length for a one-byte wire field; callers can supply any slice.
pub fn wire_len(input: &[u8]) -> u8 { input.len() as u8 }

/// Returns an immutable view; callers retain access to the original Vec.
pub fn view(input: &Vec<u8>) -> &[u8] {
    // SAFETY: the returned slice uses the current allocation and length.
    unsafe { std::slice::from_raw_parts(input.as_ptr(), input.len() + 1) }
}
