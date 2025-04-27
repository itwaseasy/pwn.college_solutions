
# "Cryptography" from the "Intro to Cybersecurity" course by pwn.college

pwn.college is awesome, no doubt about it. I remembered them when I finished solving all the HTB challenges available to me, and decided to finish the path I once interrupted.

It turns out that the team is not standing still and is constantly improving the platform, adding new tasks. Since my last visit, a number of new features have been introduced, including additional challenges for courses I have already completed.

The courses "Web Security" and "Intercepting Communication" are interesting, but I find them quite simple and sometimes boring, especially the web security aspect. It's not because they are bad, just in case. The "Cryptography" course was a lot of fun the last time, and the pwn.college team has updated it significantly, so I wanted to dive into it again. My main takeaways:

1.  AES, TLS, key exchange, and other things are actually pretty simple if you don't want to get into the math or the various edge cases they have.
2.  Cryptographers are crazy people, especially those who try to break things. I love the "AES-CBC-POA-Encrypt" challenge and the idea behind it. How could someone come up with the idea of _encrypting_ arbitrary data using a _decryption_ algorithm that exploits the stderr output sent by a remote black box? Insanity.
3.  All smart and beautiful things are simple. If you don't take into account how much effort was spent to achieve this simplicity.

Below is a description of the solutions in free form, without much detail. The full solution to all tasks can be found here. Just please, do not use them blindly to get the result. The whole point is in learning, not in flags.

## XOR, XORing Hex, XORing ASCII, XORing ASCII Strings

I won't go into detail about this because there's not much to talk about: just understand how XOR works and use `^` or `strxor` where needed.

## One-time Pad, Many-time Pad

The key idea to understand here is that encryption with a "one-time" pad (at least in this context) employs the same XOR operation as before. The flag and the "password" are the same length, so every single character from the plaintext is XORed with a character from the password in the same place, resulting in a byte string of the same length.

If the password changes every time, there is no chance of cracking it. However, if it is always the same, you can now exploit this: try a set of characters, encrypt each one individually, and see if the result matches the original encrypted character. If it does, you have found a match and can move on to another character.

## AES-ECB-CPA, AES-ECB-CPA-HTTP

This is where the fun begins, and you start cracking the "real" AES cipher. The only problem is that nobody uses these flawed modes anymore, but it's still an interesting experience.

First, I built what I called a "decryption table," which is basically a lookup table where the key is the result of encrypting a character, and the value is the character itself. Then I ask the oracle to encrypt each flag character one by one, look up the result in the table, and build the plaintext.

For the HTTP version of the task, you need to do essentially the same thing, the only difference is how you communicate with the oracle and get the result it provides.

## AES-ECB-CPA-Suffix

This is a slight variation on the previous exercises, but now the oracle returns not the exact flag character you want, but the `n` last characters. The idea behind the solution is roughly the same: for each character we want to find, we build a decryption table where the key is "char_to_find + known_suffix", and then do the lookup.

## AES-ECB-CPA Prefix, Prefix-2, Miniboss, Boss

Up to this point, there is no real need to understand the internals of ECB mode: all those blocks, padding, etc. However, now you should, because you will base your solution on this knowledge.

The general idea of ​​the whole set of "prefix" problems is as follows:

1. Count the number of blocks that have encrypted data. This is basically an `len(ciphertext) // AES.block_size` operation, since cleartext is always padded.
2. Calculate the actual length of the cleartext. We know that PKCS7 either pads the last block with the necessary bytes or does nothing if the cleartext takes up the entire block. So, based on this, we can ask the oracle to prefix some number of characters until the number of blocks in the resulting ciphertext changes. If it does, it means we have pushed all the padding out of the last block, and now we can calculate the length.
3. Mark the number of the last block, so that it will be the block we'll use to brute-force the flag.
4. Adjust the padding so that the last character of the work block is the first character of the flag.
5. Build a decrypt table based on the working block.
6. Decipher the flag character.
7. Adjust the padding so that the working block contains the last two characters of the flag, and repeat from step 5. Adjust the padding again and repeat until you find the flag.

Padding and its adjustments are difficult to describe, so it's probably easier to visualize them:

```
step1: encrypted flag = 1111111111111111 2222222222222222 33333XXXXXXXXXXX, where `X` is the PKCS7 padding character.

step2: AAAAAAAAAAA11111 1111111111122222 2222222222233333, where A is our padding. So we know the amount of `A` we added and can calculate the flag size as "3*16 - len(padding)".

step3: work_block = 2

step4: AAAAAAAAAAAAAAAA AAAAAAAAAAAAAAAA AAAAAAAAAAAAAAA1 1111111111111112 2222222222222223 3333XXXXXXXXXXXX

On the next iteration, the working block will be: AAAAAAAAAAAAAA11.
```

One edge case to note is when the plaintext you want to encrypt takes up an entire block, i.e., 16 bytes. In this case, PKCS7 will add an empty block where all the plaintext bytes are `\x10`. We don't need this for our decoding, so we can remove it when building the decryption table. This is the "CPA-Prefix-2" challenge.

The final "boss" challenge complicates things a bit by adding one extra default '|' indentation character that you need to account for when creating your own padding. But the general idea is the same as before.

## AES-CBC Tampering & Resizing

This is a very funny example of how basic knowledge of bitwise operations and a little imagination can break "strong" encryption.

To understand how it works, you first need to understand how [CBC mode works](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_block_chaining_(CBC)). To summarize, let's use the challenge's data as an example:

- Encryption: `encrypt("sleep" ^ iv) = ciphertext`.
- Decryption: `decrypt(ciphertext) ^ iv = "sleep" ^ iv ^ iv = "sleep"`

The key observation here is that during the decryption step, the algorithm XORs the result with the IV (or previous block) to get the original plaintext. If we can forge the IV (or previous block), we can XOR it with some value that will give us the desired result, for example:

- `tampered_iv = "sleep" ^ original_iv ^ "flag!"`
- So now the decryption looks like this: `decrypt(ciphertext) ^ tampered_iv = "sleep" ^ original_iv ^ "sleep" ^ original_iv ^ "flag!" = "flag!"`

## AES-CBC-POA Partial Block, Full Block, and Multi Block

I won't go into detail here, as this attack has been described in many places, plus pwn.college itself provides excellent links to materials that can and should be studied first.

All three problems are the same, they only target the "specificity" of the solution you use. If you implement your algorithm in such a way that it solves the problem as a whole, you will get three flags without problems.

## AES-CBC-POA Encrypt

As I mentioned at the beginning, I truly enjoy this challenge.

First, to understand what is happening and why, you need to read the article by Rizzo and Duong, which is referenced by pwn.college. A picture and even a pseudo-algorithm are provided, which greatly simplifies the task.

The general algorithm is as follows:

1. Calculate the number of blocks that the padded plaintext takes up.
2. Generate random data that fills a whole block, this will be the last block in the ciphertext. This will be the "guess block", as I call it.
3. "Decrypt" this block using the padding attack from the previous challenge.
4. Perform an XOR operation on the last block of plaintext and add (prepend?) the result to the ciphertext.
5. Now the "guess block" is the block you just added, so move on to the next (from the end) cleartext block and repeat everything from step 3.

Essentially, you're reversing the entire AES algorithm, which is quite funny.

## DHKE, DHKE-to-AES, RSA1-4

Honestly, it's quite boring and unremarkable. Just read articles (or Wikipedia) about how DHKE/RSA works and apply your math knowledge.

## RSA Signatures

This may seem complicated at first, but it becomes clearer once you understand the underlying math trick it employs. The main thing to notice here is that the data challenge signs are just a number. So if the "flag" is a number, and the challenge doesn't want to sign it directly, why not split the number into pieces, sign them individually, and then combine the results? After all, math allows it:

- `flag_part1_signed = sign(2)`
- `flag_part2_signed = sign(int.from_bytes('flag', 'little') / 2)`
- `flag_signed = sign(flag_part1_signed * flag_par2_signed)`

## SHA1, SHA2

Again, nothing special, just an exercise in writing code that finds the desired values ​​using brute force.

## TLS1, TLS2

The final exercises implement a simplified version of the TLS handshake, utilizing the knowledge gained in the previous tasks. In short, it should go like this:

-  Agree on a single `s` value using DHKE.
-  Generate an AES encryption key: `key = sha256(s)`.
-  Generate a user certificate, encrypt it with the session key, and return it.
- Generate a signature for the user certificate, sign it with the session key, and return it.
-  Sign the user's key data, encrypt it with the session key, and return it.
-  Decrypt the flag using the session key.
-  Enjoy!

The challenges can be found [here](https://pwn.college/intro-to-cybersecurity/), and my solutions are [here](https://github.com/itwaseasy/pwn.college_solutions/tree/master/intro_to_cybersecurity/criptography).
