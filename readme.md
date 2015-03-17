# The expletive-laden guide to Ansible

Before the swearing starts, the why and the how:

**Why another Ansible guide?** Because Ansible is a great tool, the
 existing tutorials overcomplicate the matters, and I need a better
 way to learn it.

**Why so immature?** Because I hate anything and everything remotely
 related to system administration, and need a vent. Also, I'm
 immature.

From here on, tons of swearing, so if it's not your thing, try one of
the other Ansible tutorials.

## What the fuck is Ansible?

It's a provisioning tool. That is, it does stuff on computers that you
want to repeat regularly. Its strenghts are:

* It does not need any extra shit installed on the remote computer.

* It's fast.

* And most importantly: *It's idem-fucking-potent*.

So, what the freaking fuck is idempotent? It means that Ansible is
sort-of, kind-of clever enough to figure out that whatever crap you
ask it to do, is actually not necessary, since nothing would
change. So you want to copy a fucking file from one place to another?
No need to do so, it's already there. Start some processes? They are
already running, nothing to do, move on.

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

    scp -P 2222  /Path/to/your/id_rsa.pub vagrant@127.0.0.1:/home/vagrant

If you are prompted for a password, enter `vagrant`. Now SSH into the
machine again with `vagrant ssh` from within the directory where it
was created, and run the following:

    cat id_rsa.pub >> ~/.ssh/authorized_keys

Now you should be able to SSH from anywhere on the host computer into
the VM.

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
  sudo: yes
  tasks:
    - name: Create admin user
      user: name=admini

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
`example` directory in this repo and copy your inventory into that
directory. Then run the following command:

    ansible-playbook -i inventory playbook_simple.yml

The `ansible-playbook` command runs playbooks instead of single
modules, and is where the real Ansible magic lies, so you'll be using
it much more often. When you run the above command, you should see a
list of the tasks by name, followed by information on whether anything
changed, and a final line that recaps this information.
