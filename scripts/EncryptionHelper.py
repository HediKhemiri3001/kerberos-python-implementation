

from Crypto.Cipher import AES
import json
def duplicate_string(string):
    while len(string) < 16:
        string += string
    return string[:16]

class EncryptionHelper:
    def __init__(self, context):
        self.context = context
    def write_to_logs(self,line):
        encryption_logs = open("./logs/encryption_logs.txt","a")
        encryption_logs.writelines("[%s]"%self.context + line)
        encryption_logs.close()
    def encrypt(self, payload, secret_key, initial_vector):
        # Convert the dictionary to a JSON string
        payload_str = json.dumps(payload)
        self.write_to_logs("Recieved %s to encrypt, using %s as secret key and %s as initial_vector. \n" % (payload_str,secret_key,initial_vector))
        #encryption_suite = AES.new(duplicate_string(secret_key).encode('utf8'), AES.MODE_CFB, duplicate_string(initial_vector).encode('utf8'))
        #encrypted = encryption_suite.encrypt(str(to_encrypt).encode('utf8'))
        

        # Pad the JSON string to a multiple of 16 bytes
        padded_secret_key = secret_key.ljust((len(secret_key) // 16 + 1) * 16).encode('utf8')
        padded_initial_vector = initial_vector.ljust((len(initial_vector) // 16 + 1) * 16).encode('utf8')
        # Create an AES cipher object using the secret key and initial vector
        cipher = AES.new(padded_secret_key, AES.MODE_CFB, padded_initial_vector)

        # Encrypt the padded payload using the cipher
        encrypted_payload = cipher.encrypt(payload_str.encode('utf8'))

        # Return the encrypted payload as a base64 encoded string
        
        self.write_to_logs("Encrypted to %s .\n" % str(encrypted_payload.hex()))
        return encrypted_payload.hex()
    def decrypt(self,payload, secret_key, initial_vector):
        self.write_to_logs("Recieved %s to decrypt, using %s as secret key and %s as initial_vector. \n" % (str(payload),secret_key,initial_vector))
        #decryption_suite = AES.new(duplicate_string(secret_key).encode('utf8'),AES.MODE_CFB, duplicate_string(initial_vector).encode('utf8'))
        #decrypted = decryption_suite.decrypt(str(to_decrypt).encode('utf8'))
        # Convert the payload from hex to bytes
        payload_bytes = bytes.fromhex(payload)
        padded_secret_key = secret_key.ljust((len(secret_key) // 16 + 1) * 16).encode('utf8')
        padded_initial_vector = initial_vector.ljust((len(initial_vector) // 16 + 1) * 16).encode('utf8')
        # Create an AES cipher object using the secret key and initial vector
        cipher = AES.new(padded_secret_key, AES.MODE_CFB, padded_initial_vector)

        # Decrypt the payload using the cipher
        decrypted_payload = cipher.decrypt(payload_bytes)

        # Convert the decrypted payload from bytes to a JSON string
        decrypted_str = decrypted_payload.decode('utf8').rstrip()

        # Convert the JSON string to a dictionary
        decrypted_dict = json.loads(decrypted_str)
        self.write_to_logs("Decrypted to %s .\n" % str(decrypted_dict))
        return decrypted_dict