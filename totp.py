import hmac
import hashlib
import base64
import datetime
from typing import Optional


class TOTP:
    DEFAULT_DIGITS = 6
    DEFAULT_INTERVAL = 30
    DEFAULT_ALGORITHM = 'sha1'

    def __init__(
            self,
            secret: str,
            digits: int = DEFAULT_DIGITS,
            interval: int = DEFAULT_INTERVAL,
            algorithm: str = DEFAULT_ALGORITHM
    ):
        self.digits = digits
        self.interval = interval
        self.algorithm = algorithm
        self.secret_bytes = self._decode_secret(secret)

    def _decode_secret(self, secret: str) -> bytes:
        clean_secret = secret.replace(" ", "").upper()
        padding = (8 - len(clean_secret) % 8) % 8
        padded_secret = clean_secret + '=' * padding
        return base64.b32decode(padded_secret)

    def get_time_step(self, for_time: Optional[datetime.datetime] = None) -> int:
        if for_time is None:
            for_time = datetime.datetime.now(datetime.timezone.utc)
        elif for_time.tzinfo is None:
            for_time = for_time.replace(tzinfo=datetime.timezone.utc)

        timestamp = int(for_time.timestamp())
        return timestamp // self.interval

    def generate(self, counter: int) -> str:
        msg = counter.to_bytes(8, byteorder='big')

        hmac_hash = hmac.new(
            self.secret_bytes,
            msg,
            getattr(hashlib, self.algorithm)
        ).digest()

        offset = hmac_hash[-1] & 0xF
        code_int = (
                           ((hmac_hash[offset] & 0x7F) << 24) |
                           (hmac_hash[offset + 1] << 16) |
                           (hmac_hash[offset + 2] << 8) |
                           hmac_hash[offset + 3]
                   ) % (10 ** self.digits)

        return f"{code_int:0{self.digits}d}"

    def get_current(self, for_time: Optional[datetime.datetime] = None) -> str:
        counter = self.get_time_step(for_time)
        return self.generate(counter)
