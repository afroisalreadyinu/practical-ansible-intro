# A Practical Guide to Ansible

Why another Ansible guide? Because Ansible is a great tool, but the
existing tutorials overcomplicate the matters. While trying to pick up
Ansible for provisioning servers for various side projects, I ran into
a number of issues that were not covered to sufficient detail by other
online tutorials. The aim of this tutorial is to serve as a roadmap to
programmers who want to be productive in Ansible quickly, avoiding
certain pitfalls.

## What is Ansible?

It's a provisioning tool. That is, it does stuff on computers that you
want to repeat regularly. Its strenghts are:

* It does not need any extra software installed on the remote computer.

* It's fast.

* And most importantly: *It's idempotent*.

Idempotency is a property of Ansible playbooks. As [the official
documentation
states](http://docs.ansible.com/playbooks_intro.html#tasks-list), "if
you run them again, they will make only the changes they must in order
to bring the system to the desired state."

## How the fuck do I install it?

Read their [fucking
documentation](http://docs.ansible.com/intro_installation.html).

## How the fuck do I run it?

Ansible works over SSH, so principally, you only need a computer which
you can acces over SSH. Ansible prefers authentication using private
keys instead of passwords, due to security and ease of use. If you
don't know whether you have an SSH key, just fucking google it.

In terms of on which computer to test, you have three options:

* VM

* DigitalOcean

* Some other crappy server you've put in a dingy colocation room
  somewhere, that's this close to giving its soul up, but you want to
  torture it one last time.

The recommended option is DigitalOcean. It's cheap, fast and
foolproof. Don't be a cheapass, get your credit card out and skip to
the [relevant section](#digitalocean).

Depending on which option you choose, the inventory file, the file
which tells Ansible how to reach a computer, is going to be a bit
different. These will be explained.

### VM

Fucking virtualization. Isn't it awesome that you can run a computer
in your fucking computer (xzibit.jpg), and go ape wild on it? Like
`sudo rm -rf /*` wild? It's not like the VM is running on your
computer; obviously, the memory and processing power are provided by
the VM fairies from the heavens. So let's put fucking *everything*
in VMs, the computer won't get slower when our crappy code runs in
them anyway.

If you still insist on a VM, at least use Vagrant. It makes shit
easy. [Install it](https://www.vagrantup.com/) and start the default
Ubuntu machine with `vagrant init hashicorp/precise32`. SSH into it
with `vagrant ssh`, do an `ls` or whatever silly command you can think
of to make sure it's working. All right, that was the easy part. Now
you have to copy your actual SSH key into this VM. Assuming that the
key you want to copy is in `/Path/to/your/id_rsa.pub`, run the
following command:

    scp -P 2222  /Path/to/your/id_rsa.pub vagrant@127.0.0.1:/tmp

If you are prompted for a password, enter `vagrant`. Now SSH into the
machine again with `vagrant ssh` from within the directory where it
was created, and run the following commands in order add your key to
the root account's authorized keys:

    sudo su
    mkdir -p -m 700 /root/.ssh
    cat /tmp/id_rsa.pub >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys

Now you should be able to SSH from anywhere on the host computer into
the VM as root. The default Vagrant box comes with the user `vagrant`
that has sudo rights, and one could run most of the commands we will
use for demo purposes with that user. The aim of adding the root user
is to make the following examples uniform.

Last but not least here is how the inventory file should look like:

    server ansible_ssh_port=2222 ansible_ssh_host=127.0.0.1

### <a name="digitalocean"></a>DigitalOcean

I've got no snarky comments to make about these guys. Their shit just
works. Kudos to them. One thing you have to do to use DigitalOcean is
to create an ssh key.  Go create a fucking account
[here](https://www.digitalocean.com/). The easiest way to create a
"droplet" is to use their web interface. If you do so, don't forget to
add your SSH key. It's the last box at the bottom of the form before
the "Create Droplet" button. Just copy the contents of
`~/.ssh/id_rsa.pub` or wherever you have your SSH key and paste in there.

In case you want to create and remove droplets liberally, and if you
are among the chosen few who can get a Python script with dependencies
working, you can use the `droplets.py` in this repo to create, list
and delete new DigitalOcean droplets. This script will create the
droplet with your SSH key already included, which will save you one
more step.

### Ancient computer somewhere

The only thing you need is an SSH key with which you can log in to the
remote computer, and the IP address of the computer. In this case, the
inventory file will look like the following:

    server ansible_ssh_host=A.B.C.D ansible_ssh_user=username

where `A.B.C.D` is the IP addres, and `username` is the remote
username.

### Ping it

Once you have your test server set up, run the following command to
check whether everything is working:

    ansible -i inventory server -m ping

As a response, you should see the following, anything else means you
fucked up:

    server | success >> {
        "changed": false,
        "ping": "pong"
    }

You're right, this is too much stuff for a simple ping. The
stand-alone `ansible` command is rarely used, though; it is mostly for
the purpose of testing individual modules. The above ping command does
the following: Use the inventory passed with the `-i` argument to run
the module passed with the `-m` argument. You're thinking "WTF is a
module", just be patient for another fucking minute, OK? The ping
module does not need any arguments, but if it did, it would have been
possible to pass them with another switch. But as mentioned, we are
interested in more complicated stuff and not a shitty replacement for
`ssh -c`, so read on for plays, roles, and more.

## Plays, Modules, etc

There are only four fundamental concepts necessary for grokking
Ansible; if you understand these, you're halfway there. To make it as
simple as possible, here is a plaing fucking list:

* **Modules** are units of action. For pretty much everything you
    would do on a server, there is a module. They can be built-in or
    add-ons. Examples are ping, copy/modify/delete file, install
    packages, start/stop/restart a service etc.

* **Inventory** is the specification of a set of servers. Ansible
    provides very convenient ways to specify sets of servers, and
    aliases for these.

* **Roles** are collections of actions that serve a purpose, like
    installing, configuring and then starting a database server, or
    retrieving code, building it, moving it to servers and runing it.

* **Playbooks** are collections of actions to run on a cluster of
    servers. Plays also contain data to make sure that the pieces fit
    together.

So in effect, **roles are collections of module applications, and
playbooks are specifications of which roles should be matched to which
inventory**. Module application means that a module is applied to a
host with some arguments.

A sidenote: In the [official
documentation](http://docs.ansible.com/playbooks.html) it says that
"Playbooks are Ansible’s configuration, deployment, and orchestration
language". What kind of retarded bullshit technical writing is this?
Playbooks are not the fucking language, they are what you write in the
fucking language. Can't they pay for a fucking technical writer? Or
even an editor? Or just some sane person with a fucking highschool
degree who can proofread their shit? For fucks sake.

### Writing plays & roles

OK, let's get going. The example I want to cover here is the average
case of an RDBMS-driven website running on Python. What do we need on
this server? Well, first of all, you need to forbid root SSH access,
and create an admin user with sudo rights who is allowed to do rooty
stuff instead. The gods of sysadministan have agreed that this is the
right thing to do; who are we to contest that?  Not that it sinks your
server's chances of getting hacked, but I don't want to be the one
responsible if it happens.

Here is how a concise playbook that achieves this looks like:

```yml
- hosts: server
  remote_user: root
  sudo: yes
  tasks:
    - name: Create admin user
      user: name=admini shell=/bin/bash

    - name: Sudo rights for admini
      lineinfile: dest=/etc/sudoers state=present regexp='^admini' line='admini ALL=(ALL) NOPASSWD:ALL'

    - name: Copy SSH key to admini
      authorized_key: user=admini key="{{ lookup('file', '~/.ssh/id_rsa.pub') }}"

    - name: Remove root ssh login
      lineinfile: dest=/etc/ssh/sshd_config regexp="^PermitRootLogin" line="PermitRootLogin no" state=present
```

You're probably asking yourself about the format. It's YAML, yet
another markup language. The good things about it: it's neither XML
nor JSON. The bad thing: It's a fucking markup language, and sometimes
you have to bend over backwards to get what the crappiest programming
language would get done in two lines of code. That's the way Ansible
rolls, so you'll have to deal with it. In this simple example, we are
listing the tasks within the playbook, which should be OK for a small
provisioning exercise, but it should be obvious that as the number of
tasks grows, and the inventory specification gets more complicated,
this method will not work. Each task has a name, which is more like a
description, and a specification on the next line. The specification
starts with the name of a module, and continues with parameters as
fields. [This list of all available ansible
modules](http://docs.ansible.com/list_of_all_modules.html) should
leave no doubts that pretty much every need can be served out of the
box.

In order to run the above playbook, save it in a file named
`playbook_simple.yml` next to the inventory. Or just navigate to the
`examples/part1` directory in this repo and copy your inventory into
that directory. Then run the following command:

    ansible-playbook -i inventory playbook_simple.yml

The `ansible-playbook` command runs playbooks instead of single
modules, and is where the real Ansible magic lies, so you'll be using
it much more often. When you run the above command, you should see a
list of the tasks by name, followed by information on whether anything
changed, and a final line that recaps this information. Here is what
you should see when you run `playbook_simple.yml` for the first time
on a fresh server:

    PLAY RECAP **********************************************************
    server           : ok=5    changed=4    unreachable=0    failed=0

Among the 4 tasks we had in our playbook, all have been executed, and
led to changes in the system, thus the entry `changed=4`. If we run
the same playbook once more, however, here is what we see:

    PLAY RECAP ************************************************************
    server             : ok=5    changed=0    unreachable=0    failed=0

Now, `changed=0`, because the tasks do not have to be run, as they
would not lead to any changes in the system. This is what is meant
with *idempotent*; running this playbook (and ideally any playbook)
will not lead to a different system, no matter how many times you've
already run it.

## Who is Ansible on my server?

One thing that is relatively confusing with Ansible is who the fuck
you actually are on a server. There are a number of different configs,
command line switches, and playbook options that have an effect on the
user Ansible runs commands as. Here is a tiny playbook that we will
use to print the Ansible user (can be found in
`examples/part1/whoami.yml`):

```yml
- hosts: server
  remote_user: admini
  tasks:
    - name: Print the actual user
      command: whoami
```

In order to also see the output of this command, you have to run the
playbook command with the next level of verbosity:

    ansible-playbook -i inventory whoami.py -v

Here is the output we should see when we run this playbook on the
server that we provisioned with `playbook_simple.py`:

```
# bla bla bla....
TASK: [Print the actual user] *************************************************
changed: [server] => {"changed": true, "cmd": ["whoami"], "delta": "0:00:00.002952", "end": "2015-03-21 20:54:58.971190", "rc": 0, "start": "2015-03-21 20:54:58.968238", "stderr": "", "stdout": "admini"}

# a little more bla bla
```

This input will be a bit more bowine if you have the `cowsay` command
installed. So the `remote_user` instruction works; we are in fact
`admini` on the server. But what if we wanted to run a command that
requires sudo? In that case, we simply add the `sudo: true` option,
with the playbook now looking like this:

```yml
- hosts: server
  remote_user: admini
  sudo: true
  tasks:
    - name: Print the actual user
      command: whoami
```

which leads to the following output:

```
TASK: [Print the actual user] *************************************************
changed: [server] => {"changed": true, "cmd": ["whoami"], "delta": "0:00:00.001985", "end": "2015-03-21 20:56:51.932011", "rc": 0, "start": "2015-03-21 20:56:51.930026", "stderr": "", "stdout": "root"}
```

The default user which Ansible sudo's as is, understandably,
root. This can be changed, though, with the `sudo_user` instruction.

Supplying the user to connect as in each and every playbook can be
cumbersome and error-prone if you have many of them, so Ansible offers
an easy way to set a default for all playbooks in a directory, by
creating an `ansible.cfg` file and putting the following in there:

```
[defaults]
remote_user = admini
```

If you don't specify another remote user in a playbook, this option in
the config file will be used to determine which user to SSH as. There
are two more ways to specify the remote user. These are:

- As a command line option to `ansible-playbook`, with the switch `-u`

- As a part of the inventory, with the property `ansible_ssh_user`

The precedence of these options is as follows:

    inventory > playbook > command line > ansible.cfg

That is, specification in the inventory overrides everything else,
whereas the default value in `ansible.cfg` is, as the name implies,
only a default.

## Roles

Now that we have the basics covered, let's actually start provisioning
the server. We will start by installing a number of packages that we
need for the above mentioned scenario of RDBMS-driven website in
Python. The packages we need are PostgresSQL, Nginx, Git and
virtualenv. Before we install these, though, it makes sense to update
the apt cache to get the latest versions of these packages. Here is a
playbook that does all of these
(`example/part1/install_packages.yml`):

```yml
- hosts: server
  sudo: yes
  tasks:

    - name: Update apt cache
      apt: update_cache=yes

    - name: Install required packages
      apt: pkg={{ item }}
      with_items:
        - nginx
        - postgresql
        - git
```

Alright, we have ourselves a web and a database server, and the tools
to check out our code. Now we need to go ahead and actually check out
our code, and do stuff with it. It would be rather messy if we
continued adding more tasks into this play, however, not to mention
how we organize the configuration files and templates that will come
up later. Therefore, let's take the step mentioned earlier and
separate out our playbooks into roles. A role gathers tasks that are
conceptually coherent, and bundles them with some other things like
data and triggers. Roles reside in the `roles` directory next to
playbooks, and have the following file structure:

```yml
playbook.yml
roles/
    common/
        tasks/
            main.yml
        handlers/
            main.yml
    dbserver/
        tasks/
            main.yml
        handlers/
            main.yml
        files/
            pg_config.cfg
        templates/
            pg_hba.conf.j2
```

There are some new directory names there. The first is
`handlers`. These are triggers that can be registered with tasks, such
as reloading nginx configuration or restarting a service when it's
redeployed. The files that contain the tasks and handlers should be
named `main.yml`, meaning that you will end up with twice as many
`main.yml` files as you have roles, which honestly sucks. The third
directory, `files`, is for storing any files that have to be copied to
servers as-is. The `templates` directory contains Jinja2 templates
that need to be rendered before getting copied on to the server.

Let's move the tasks above that installed packages into a role called
`packages`, and use it in a playbook. You can find the playbook and
the roles in the directory `example/part2`. As you can see, the
directory tree becomes rather convoluted even for the simplest
role-based organization, but again, this is how Ansible rolls. Here is
how `roles/packages/tasks/main.yml` looks:

```yml
- name: Update apt cache
  sudo: true
  apt: update_cache=yes

- name: Ensure all required locales are present
  locale_gen: name="en_US.UTF-8" state=present

- name: set locale to UTF-8
  sudo: true
  command: /usr/sbin/update-locale LANG="en_US.UTF-8" LC_ALL="en_US.UTF-8" LANGUAGE="en_US.UTF-8"

- name: Install required packages
  sudo: true
  apt: pkg={{ item }}
  with_items:
    - nginx
    - postgresql
    - python-psycopg2 #also required by ansible
    - git
    - python-virtualenv
    - python-dev
    - postgresql-server-dev-9.1
```

This role, which installs the usual Debian packagese a Python web
application needs, is relatively straightforward, with the exception
of a loop in the last task. The `with_items` option enables looping a
task over a list, and replacing `{{ item }}` with the elements of that
list. This is equivalent to repeating the task with the list
elements. The double curly braces is the syntax used by Jinja2 for
inserting variables. You can use similar variable substitution pretty
much anywhere in Ansible, but the more advanced uses of Jinja2 is
restricted to actual templates. In role and play definitions, only
variable substitution is allowed.

We can include the above role in a playbook by listing it among the
`roles` attribute of a play. Here's the section in the `site.yml`
playbook where this happens:

```yml
- hosts: server
  vars:
    db_password: test
  roles:
    - packages
    - db
```

`site.yml` playbook consists of two plays. A play is a combination of
hosts, roles, variables, and other configuration options such as
`remote_user` or `sudo`.

## Handlers

The `db` role does two things: copy an alternative Postgres
authentication configuration file (`pg_hba.conf`) onto the server,
creating a time-stamped backup if it differs, and adding a new admini
user. The first of these two actions requires a restart of the
Postgres server. We could add this as a manual step after the
configuration file is copied over, but a better idea is to have a
handler that is triggered whenever an action requiring a restart of
the Postgres server is executed. Such triggers go into the
`handlers/main.yml` file in a role directory, and should have a format
as follows:

```yml
- name: restart postgres
  sudo: yes
  service: name=postgresql state=restarted
```

This handler can then be referenced from a role in the `notify` field:

```yml
- name: Postgres access
  copy: src=pg_hba.conf dest=/etc/postgresql/9.1/main/pg_hba.conf owner=postgres backup=yes
  sudo: yes
  notify:
    - restart postgres
```

A nice feature of handlers is that they will be triggered once in a
single play. That is, if you change a configuration multiple times,
the service will be restarted only once, at the end of the play, and
not with each configuration change.

## Variables

Variables in Ansible are what you would expect: can be defined in many
different ways, such as:

- In the inventory
- In a play
- As arguments to included tasks and roles