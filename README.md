# StrangeOS

Basic UNIX-like os build in python

## Technologies

-   Python
-   SQLite

## How to start?

-   To run os run [run script](run) or execute:

```bash
 python src/boot.py
```

-   To clear filesystem data run [clear script](clear) or remove `filesystem.db`

## Information about system

Help with commands you will find in [help file](./src/data/helpmsg.txt) or by typing `help` in os itself.

### Filesystem base structure:

```
root
|-- bin
|   `-- hi
|-- etc
|   `-- help.txt
|-- home
|   `-- root
|       `-- hello.txt
```

### System options scheme:

Options must be saved in `options.json` file in root project directory. [Options template](options.template.json) provides default options for you to change

```
{
    # System name
    sysname: str ("system")

    # Initial password to root user
    rootpassword: str ("")

    # Directory to filesystem database
    dbdir: str ("filesystem.db")

    # If true displays verbose error messages
    verbose: bool (False)

    # If true displays instruction segments
    segments: bool (False)
}
```

> &lt;option&gt;: &lt;type&gt; (&lt;default value&gt;)
