
---

**XML External Entity (XXE) Attack**

This is a security vulnerability that abuses XML data parsers. It often allows an attacker to interact with any backend interface or external systems that the application itself can access, and can allow the attacker to read files present on that system.

Before we begin, let's get to know XML:
XML is a markup language formatted in a way that both machines and humans can read. It is used to store and transfer data. Every XML document typically begins with what is known as the **XML Prolog**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
```

This line specifies the XML version and the encoding used in the document. It is not mandatory but is preferred. Every XML document must contain a **root element**, inside which come what are called **child elements**. Attributes can also be used and come in this form:

```xml
<text category = "message">You need to learn about XXE</text>
```
- `category` is the attribute name
- `message` is the attribute value

---

I will explain another important concept called **DTD** (Document Type Definition). It defines the structure, elements, and valid attributes of an XML document:

```xml
<!DOCTYPE note [ <!ELEMENT note (to,from,heading,body)> <!ELEMENT to (#PCDATA)> <!ELEMENT from (#PCDATA)> <!ELEMENT heading (#PCDATA)> <!ELEMENT body (#PCDATA)> ]>
```

So now let's understand how that DTD validates the XML. Here's what all those terms used in note.dtd mean:

- `!DOCTYPE note` — Defines a root element of the document named note
- `!ELEMENT note` — Defines that the note element must contain the elements: "to, from, heading, body"
- `!ELEMENT to` — Defines the to element to be of type "#PCDATA"
- `!ELEMENT from` — Defines the from element to be of type "#PCDATA"
- `!ELEMENT heading` — Defines the heading element to be of type "#PCDATA"
- `!ELEMENT body` — Defines the body element to be of type "#PCDATA"

**NOTE:** #PCDATA means parseable character data.

---

**Now we will look at the XXE payload and how it works:**

```xml
<?xml version="1.0"?>
<!DOCTYPE root [<!ENTITY read SYSTEM 'file:///etc/passwd'>]>
<root>&read;</root>
```

We defined the entity and set its value to `SYSTEM`, then provided the path of the file we want to read. If the application is vulnerable to an XXE attack, it will display the contents of the specified file.

---

**The following payload prints a name on the screen:**

```xml
<!DOCTYPE replace [<!ENTITY name "feast"> ]>
<userInfo>
  <firstName>falcon</firstName>
  <lastName>&name;</lastName>
</userInfo>
```
