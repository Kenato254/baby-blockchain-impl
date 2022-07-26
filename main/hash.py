from hashlib import sha1

class SHA1:
    """The algorithm used in this class is from python's built-in library hashlib as recommended to save time."""

    def toSHA1(self, string: bytes):
        """
        a function that takes a string of data as input and returns a hash value of this data in the form of a string 
        (in this case, the SHA1 function with a length of 160 bits is used as a hashing algorithm).

        :string:
            string input
        """
        return sha1(string).hexdigest()



if __name__ == "__main__":
    h = SHA1()
    print(h.toSHA1(b"hello world"))
    print(h.toSHA1(b"hello world0"))
    print(h.toSHA1(b"hello world9999"))
