/// Returns the first byte, or None for empty input.
pub fn first(input: &[u8]) -> Option<u8> { input.first().copied() }

/// Returns the length for a one-byte wire field.
///
/// # Errors
/// Returns an error when the length exceeds 255.
pub fn wire_len(input: &[u8]) -> Result<u8, std::num::TryFromIntError> {
    u8::try_from(input.len())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn boundary_contracts() {
        assert_eq!(first(&[]), None);
        assert_eq!(first(&[42]), Some(42));
        assert_eq!(wire_len(&[0; 255]), Ok(255));
        assert!(wire_len(&[0; 256]).is_err());
    }
}
