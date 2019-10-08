import os
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from .settings import Settings
from .logger import Logger

log = Logger.get(__name__)

key_file = Settings.secret_key_location
key = None
try:
  if not os.path.isfile(key_file):
    log.info('Key file not found.')
    key = get_random_bytes(16) # 16 bytes
    with open(key_file, "wb") as file_out:
      file_out.write(key)
      log.info('Key file created.')
  elif not key:
    with open(key_file, "rb") as kf:
      key = kf.read()
    log.info('Key file exists and opened.')
  else:
    log.info('Key already loaded.')
except Exception as exc:
  log.error(exc, exc_info=True)

class EncryptionUnit:
  errors = 'ignore'
  def __init__(self, data, tag=None, nonce=None):
    self.data = data
    self.tag = tag
    self.nonce = nonce
  def encrypt(self):
    try:
      cipher = AES.new(key, AES.MODE_EAX)
      data = self.data.encode(errors=self.errors)
      ciphertext, tag = cipher.encrypt_and_digest(data)
      self.nonce = cipher.nonce
      self.tag = tag
      self.data = ciphertext
    except Exception as exc:
      log.error(exc, exc_info=True)
    return self
  def decrypt(self):
    try:
      cipher = AES.new(key, AES.MODE_EAX, self.nonce)
      decrypted_data = cipher.decrypt_and_verify(self.data, self.tag)
      self.data = decrypted_data.decode(errors=self.errors)
    except Exception as exc:
      log.error(exc, exc_info=True)
    return self
  @classmethod
  def get_hash(cls, plain_data):
    hash_object = hashlib.sha256(plain_data.encode(errors=cls.errors))
    return hash_object.hexdigest()

# if __name__ == '__main__':
  # Test
  # try:
  #   data_test = "TestPassword123!3$-4o3245$%"
  #   enc_data = EncryptionUnit(data_test).encrypt()
  #   dec_data = EncryptionUnit(enc_data.data, enc_data.tag, enc_data.nonce).decrypt()
  #   if data_test != dec_data.data:
  #     log.error("Encryption / decryption test failed.", exc_info=True)
  # except Exception as exc:
  #   log.error(exc, exc_info=True)

