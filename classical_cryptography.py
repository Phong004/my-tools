import os
import math

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def caesar_encrypt(plain, key):
    cipher = ''
    key = int(key) if isinstance(key,int) or ord(key[0]) in range (48,58) else ord(key.strip().lower())%97
    key %= 26
    for p in plain.strip().lower():
        cipher += alphabet[(ord(p)%97+key)%26]
    return cipher

def caesar_decrypt(cipher, key):
    plain = ''
    key = int(key) if isinstance(key,int) or ord(key[0]) in range (48,58) else ord(key.strip().lower())%97
    key %= 26
    for c in cipher.strip().lower():
        plain += alphabet[(ord(c)%97-key)%26]
    return plain

def vigenere_encrypt(plain:str, list_keys: list) -> str:
    cipher = ''
    keys = [ord(k.strip().lower())%97%26 if isinstance(k,str) else int(k)%26 if isinstance(k,int) or ord(k[0]) in range(48,58) else None for k in list_keys]
    for k in keys:
        if k == None: raise("List of keys contains an invalid key")
    for i in range(len(plain)):
        cipher += alphabet[(ord(plain[i].strip().lower())%97+keys[i%len(keys)])%26] if plain[i].isalpha() else plain[i]
    return cipher

def vigenere_decrypt(cipher:str, list_keys:list) -> str:
    plain = ''
    keys = [ord(k.strip().lower())%97%26 if isinstance(k,str) else k%26 if isinstance(k,int) or ord(k[0]) in range(48,58) else None for k in list_keys]
    for k in keys:
        if k == None: raise("List of keys contains an invalid key")
    for i in range(len(cipher)):
        plain += alphabet[(ord(cipher[i].strip().lower())%97-keys[i%len(keys)])%26] if cipher[i].isalpha() else cipher[i]
    return plain

def affine_encrypt(plain:str, key_a:int, key_b:int) -> str:
    cipher = ''
    key_a %= 26
    key_b %= 26
    if math.gcd(key_a, 26) != 1:
        raise ("a must be relative prime number of 26")
    cipher = ''.join([alphabet[((key_a*(ord(p)%97)%26+key_b))%26] if p.isalpha() else p for p in plain.strip().lower()])
    return cipher

def inverse_a(a:int, m:int) -> int:
    r_old, r_new = m, a
    t_old, t_new = 0, 1
    while r_new > 0:
        q = r_old//r_new
        r_old, r_new = r_new, r_old - q*r_new
        t_old, t_new = t_new, t_old - q*t_new
    return t_old%m

def affine_decrypt(cipher: str, key_a:int, key_b:int) -> str:
    plain = ''
    key_a %= 26
    key_b %= 26
    if math.gcd(key_a, 26) != 1:
        raise ("a must be relative prime number of 26")
    inv_a = inverse_a(key_a, 26)
    plain = ''.join([alphabet[inv_a*(ord(c)%97-key_b)%26] if c.isalpha() else c for c in cipher.strip().lower()])
    return plain

def railfence_encrypt(plain:str, key:int):
    plain = plain.strip().upper()
    if key == 1: return plain
    cipher = ''
    key %= len(plain)
    T = 2*(key-1)
    for r in range(key):
        index = r
        check = True
        while index < len(plain):
            cipher += plain[index]
            if r == 0 or r == key-1:
                step = T
            elif check:
                step = T - 2*r
            else:
                step = 2*r
            index += step
            check = not check
    return cipher

def railfence_decrypt(cipher:str, key:int):
    cipher = cipher.strip().upper()
    if key == 1: return cipher
    plain = [""]*len(cipher)
    key %= len(cipher)
    T = 2*(key-1)
    j = 0
    for r in range(key):
        i = r
        check = True
        while i < len(cipher):
            plain[i] = cipher[j]
            if r == 0 or r == key-1:
                step = T
            elif check:
                step = T - 2*r
            else:
                step = 2*r
            i += step
            j += 1
            check = not check
    return ''.join(plain)

def coltrans_encrypt(plain:str, keys:list):
    plain = plain.strip().upper()
    cipher = ''
    keys = [(k-1)%len(keys) if isinstance(k,int) else ord(k.strip().lower())%97%26 if isinstance(k,str) else None for k in keys]
    cols_num = len(keys)
    cols = [""] * cols_num
    rows_num = len(plain)//cols_num
    remainder = len(plain)%cols_num
    plain += "X"*remainder
    rows_num += 1 if remainder!=0 else 0
    for i,char in enumerate(plain):
        col_idx = i%cols_num
        cols[col_idx] += char
    cols_trans = list(zip(keys,cols))
    cols_trans.sort()
    cipher = ''.join([c[1] for c in cols_trans])
    return cipher

def coltrans_decrypt(cipher:str, keys:list):
    cipher = cipher.strip().upper()
    plain = ''
    keys = [(k-1)%len(keys) if isinstance(k,int) else ord(k.strip().lower())%97%26 if isinstance(k,str) else None for k in keys]
    cols_num = len(keys)
    rows_num = len(cipher) // cols_num
    cols_index = []
    for ori_index, key in enumerate(keys):
        cols_index.append((key,ori_index))
    sorted_key = sorted(cols_index)
    recons_cols = [""] * cols_num
    cur_idx = 0
    for tmp,ori_index in sorted_key:
        chunk = cipher[cur_idx:cur_idx+rows_num]
        recons_cols[ori_index] = chunk
        cur_idx += rows_num
    for r in range(rows_num):
        for c in range(cols_num):
            plain += recons_cols[c][r]
    return plain.rstrip("X")

# cipher = vigenere_encrypt('hello123', 'abcdef')
# decrypt = vigenere_decrypt(cipher, 'abcdef')

# cipher = affine_encrypt('hello123', 5, 12)
# decrypt = affine_decrypt(cipher, 5, 12)

# cipher = railfence_encrypt('HelloWorld', 3)
# decrypt = railfence_decrypt(cipher, 3)

# cipher = coltrans_encrypt('helloworld', [3,2,4,1])
# decrypt = coltrans_decrypt(cipher, [3,2,4,1])
cipher = railfence_encrypt("MEETMELATER", 4)
decrypt = railfence_decrypt(cipher, 4)


print (cipher, decrypt)