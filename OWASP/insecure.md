
---

**Insecure Deserialization**

This definition is still very broad — it is the replacement of data processed by an application with malicious code. Using DOS and RCE, it can be used to gain a foothold in pentesting.

---

**Objects:**
Objects allow you to create short, similar lines of code without having to write all those lines manually.

---

**De(Serialization):**
Serialization is the process of converting objects used in programming into a simpler, compatible format for transmission between systems or networks for further processing or storage. This format is in binary form — 0s and 1s.

---

**Cookies 101:**
Cookies are an essential tool for modern websites to function. They are small pieces of data, created by a website and stored on the user's computer.

You can view your cookie information via:
`Inspect → Storage`

Cookies are most often encoded in **Base64**. This website decodes that type of encoding: https://www.base64decode.org/

If the website is not protected via HTTPS, this means we can do some fun things — like changing your user privilege to **admin**.

---

**A more advanced attack beyond just decoding cookies — let's get into the core details:**

First, let's assume a normal user privilege level. We create an account on our target, then if there is another login form we go to it — it will be vulnerable because if the user is required to enter their notes, the data will be encoded and sent to the Flask application no matter what type it is. If the target uses Python with its default database framework Flask, it will accept the input and treat the data as trusted. But we are hackers and will use the following methods to exploit the vulnerability:

This vulnerability works at its core because the database was written using one of Python's libraries, and we will use this library for reverse reading.

First, we go to the command panel and run the following listening command:

```
nc -lvnp 4444
```

Then we open the file related to this vulnerability called **pickleme.py**, enter the IP used in the browser for this process, then run the script and copy the code that appears — copy what is between the tags — then go to the website:

`Inspect → Storage`

And paste the code inside the `encode` field, then reload the page and go back to the listening window. We will find that we have gained access to the targeted database and can run commands inside it such as `whoami`, `pwd`, etc.
