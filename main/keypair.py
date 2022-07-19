# ? Built-ins
import sys
import os
import base64
import pyasn1.codec.der.encoder
import pyasn1.type.univ
from pprint import pprint
from dataclasses import dataclass, field, asdict
from typing import Any, Generic, NewType, Optional

# ? Third Party Libraries
import numpy as np
from Crypto.Math.Primality import generate_probable_prime, generate_probable_safe_prime
from Crypto.Math.Numbers import Integer

# * Typing class for Prime Number
Prime = NewType("Prime", int)
Prime1 = NewType("Prime1", Prime)
Prime2 = NewType("Prime2", Prime)
PrivateExponent = NewType("PrivateExponent", int)
PublicExponent = NewType("PublicExponent", int)
Modulus = NewType("Modulus", int)


@dataclass
class KeyPair:
    """Simple RSA Algorithim to Compute KeyPair"""

    __private_key: tuple[PrivateExponent, Modulus] | None = None
    __large_primes: tuple[Prime1, Prime2] | None = None
    public_key: tuple[Modulus, PublicExponent] | None = None
    key_bytes: Optional[int] = field(default=1024)

    @classmethod
    def from_existing(cls, kprv, p_q, kpub, k_bytes) -> "KeyPair":
        """Returns a new object of KeyPair generated from Private Key"""
        return cls(kprv, p_q, kpub, k_bytes)

    @property
    def get_private_key(self) -> tuple[PrivateExponent, Modulus]:
        return self.__private_key

    @property
    def get_primes(self) -> tuple[Prime1, Prime2]:
        """
        Generates primes p & q: for automation purposes.
        Using third party package pycryptodome with optimize Primality Tests
        """
        Primes: set = set()

        while len(Primes) != 2:
            rand_prime: int = int(generate_probable_prime(exact_bits=self.key_bytes))
            Primes.add(rand_prime)
        self.__large_primes = tuple(Primes)
        return self.__large_primes

    def gen_key_pair(
        self, e: PublicExponent = 65537
    ) -> dict[str, tuple[PrivateExponent, Modulus] | tuple[Modulus, PublicExponent]]:
        """
        Generates keys which return an object of the KeyPair class

        :str:
            Key for accessing private or public key.

            :Kpr:
                Private key access key-value
            :Kpub:
                Public key access key-value
        """

        # * Get Fairly large primes p & q
        temp1, temp2 = self.get_primes  # * Fairly size key
        p, q = np.array(temp1, dtype="O"), np.array(temp2, dtype="O")
        del temp1, temp2

        # * n: Product of p * q
        n = np.multiply(p, q, dtype="O")

        # * Compute phi of n = (p-1)(q-1) which is basically number of coprimes with n.
        phi_of_n = np.multiply((p - 1), (q - 1), dtype="O")

        # * Kpub = e. From members of set {2, 3, ... phi(n  -1)} such that g.c.d(e, phi(n)) = 1

        while e < phi_of_n:
            if np.gcd(e, phi_of_n) == 1:  #
                self.public_key = (n, e)  # * Public Key: Kpub = (n, e)
                break
            e += 1

        # * Compute Kpr = d, such that d * e mod phi(n) = 1
        lcm = Integer((p - 1)).lcm(q - 1)
        d = Integer(e).inverse(lcm)
        self.__private_key = (int(d), n)
        return {"Kpr": self.get_private_key, "Kpub": self.public_key}

    def __format_key(self, n, e, d, p, q, dP, dQ, qInv, **kwargs):
        """DER: Binary Encoding. PEM: Base64 encoding"""

        if kwargs.get("key", None) == "Private":  # * Private-DER
            # ASN.1 specification:
            # PrivateKey ::= SEQUENCE {
            # version           Version,
            # modulus           INTEGER,  -- n
            # publicExponent    INTEGER,  -- e
            # privateExponent   INTEGER,  -- d
            # prime1            INTEGER,  -- p
            # prime2            INTEGER,  -- q
            # exponent1         INTEGER,  -- d mod (p-1)
            # exponent2         INTEGER,  -- d mod (q-1)
            # coefficient       INTEGER,  -- (inverse of q) mod p
            # }
            seq = pyasn1.type.univ.Sequence()
            for i, x in enumerate((0, n, e, d, p, q, dP, dQ, qInv)):
                seq.setComponentByPosition(i, pyasn1.type.univ.Integer(x))
            der = pyasn1.codec.der.encoder.encode(seq)

            if kwargs.get("format", None) == "PEM":
                template = "--------------------BEGIN RSA PRIVATE KEY--------------------\n{}--------------------END RSA PRIVATE KEY--------------------\n"
                return template.format(base64.encodebytes(der).decode("ascii"))
            return der

        elif kwargs.get("key", None) == "Public":
            # ASN.1 specification:
            # RSAPublicKey ::= SEQUENCE {
            #     modulus           INTEGER,  -- n
            #     publicExponent    INTEGER   -- e
            # }
            seq = pyasn1.type.univ.Sequence()
            for i, x in enumerate((n, e)):
                seq.setComponentByPosition(i, pyasn1.type.univ.Integer(x))
            der = pyasn1.codec.der.encoder.encode(seq)

            if kwargs.get("format", None) == "PEM":  # * PEM
                template = "--------------------BEGIN RSA PUBLIC KEY--------------------\n{}--------------------END RSA PUBLIC KEY----------------------\n"
                return template.format(base64.encodebytes(der).decode("ascii"))
            return der
        else:
            raise ValueError(
                "Unknown key format '%s'. Cannot export the RSA key." % format
            )

    def to_string(self, **kwargs) -> str | bytes:
        """function that allows you to form a string from the objects of a key pair.
        Returns an object of the String class.
        """
        args: tuple = (
            *self.public_key,
            self.get_private_key[0],
            *self.get_primes,
            self.get_private_key[0] % (self.get_primes[0] - 1),
            self.get_private_key[0] % (self.get_primes[1] - 1),
            Integer(self.get_primes[0]).inverse(self.get_primes[1]),
        )
        if not kwargs:
            kwargs.update({"key": "Private", "format": "DER"})
            str_prv = self.__format_key(*args, **kwargs)
            kwargs.update({"key": "Public"})
            str_pub = self.__format_key(*args, **kwargs)
            return str_prv, str_pub
        else:
            return self.__format_key(*args, **kwargs)

    def print_key_pair(self, **kwargs) -> None:
        """Output the objects of the key pair.

        Private Key
        -----------
        To print Public Key in DER-Format; Pass key="Private" to the method.
            Example: print_key_pair(key="Private")

            To print Public Key in PEM-Format; Pass key="Private" and format="PEM" to the method.
                Example: print_key_pair(key="Private", format="PEM")

        Public Key
        ----------
        Substitute "Private" with "Public" to achieve same output for Public Key.

        KeyPair
        -------
        Pass no argument to output both "Private Key" and "Public Key" in "DER"'s format respectively.
        """

        if not kwargs:
            print(
                "-------------Private Key-----------",
                *self.to_string(),
                sep="\n\n -------------Public Key-----------  \n"
            )
        else:
            print(self.to_string(**kwargs))


if __name__ == "__main__":
    keypair = KeyPair(1024)
    pr, pub = keypair.gen_key_pair().values()
    # keypair.print_key_pair(key="Public", format="PEM")
    # keypair.print_key_pair()
    # print(f"{keypair.get_primes =}")
    # print("\n\n")
    new_keys = keypair.gen_key_pair(e=pr[0])
    # print(f"{keypair.get_primes =}")
    # print("\n\n")
    # pprint(new_keys)
    # print(keypair.key_bytes)
    keypair2 = keypair.from_existing(
        new_keys["Kpr"],
        keypair.get_primes,
        new_keys["Kpub"],
        keypair.key_bytes,
    )
    keypair2.print_key_pair(key="Private", format="PEM")
