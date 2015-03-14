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
to create an ssh key.
Go create a fucking account [here](https://www.digitalocean.com/). You
can then either use their web interface to create a "droplet" (let's
invent our own name instead of calling them fucking virtual machines
or servers, not that it costs us anything, right?).

### Ancient computer somewhere

The only thing you need is an SSH key with which you can log in to the
remote computer, and the IP address of the computer. In this case, the
inventory file will look like the following:

    server ansible_ssh_host=A.B.C.D ansible_ssh_user=username

where `A.B.C.D` is the IP addres, and username is the remote username.

## Ping it

Run the following command:

    ansible -i inventory server -m ping

You're right, this is too much stuff for a simple ping. But keep in
mind two things:

* Ansible was written for big-ass server infrastructure automation, a
  puny ping is too insignificant to simplify.

* The `ansible` command is used only for testing individual modules
  like `ping`, not for actually automating stuff.

WTF is a module, you say? Here is the very basics of how Ansible is
organized.