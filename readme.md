# A Practical Introduction to Ansible

Ansible is a great tool that can be used for the orchestration of
server clusters of all sizes, from a single computer to a huge farm.
While trying to pick up Ansible to provision servers for various side
projects, I ran into a number of issues that were not covered to
sufficient detail by other online tutorials. The aim of this tutorial
is to serve as a roadmap to programmers who want to understand the
central concepts and be productive in Ansible quickly, while avoiding
such pitfalls.

## What is Ansible?

It's a provisioning tool. That is, it does stuff on computers that you
want to repeat regularly. Ansible's strenghts are:

* It does not need any extra software installed on the remote computer.

* It's fast.

* And most importantly: *It's idempotent*.

Idempotency is a property of Ansible playbooks. As [the official
documentation
states](http://docs.ansible.com/playbooks_intro.html#tasks-list), "if
you run them again, they will make only the changes they must in order
to bring the system to the desired state."

## How do I install it?

If you are a Python developer and have virtualenv installed, it's as
simple as creating a virtualenv and then running `pip install ansible`
inside it. Otherwise, refer to the [official
documentation](http://docs.ansible.com/intro_installation.html).

## How do I run it?

Ansible works over SSH, and does not require any special software
installed on the remote server. Principally, you only need a Linux
instance which you can acces over SSH. The prefered method of
authentication is using private keys instead of passwords, due to
security and ease of use. The collection of servers on which an
Ansible playbook should run is specified in what is called the
**inventory**. The inventory lists the names of the computers together
with connection information such as SSH port and IP address. If you
already have a server to which you can SSH as root on the default
port, here is what you should put into a file named `inventory`:

    server ansible_ssh_host=IP_ADRESS

A sample inventory file is included in the `example` directory within
this repo, within which we will be running the sample playbooks. You
can go ahead and change it to suit your setup. Since we will be
modifying the system quite a bit, you are recommended to use a server
you can wipe and reinstall at will. The easiest way to do this is to
use a VM, either locally or from a provider. Depending on which option
you choose, the inventory file is going to be a bit different.

### VM

The easiest way to create and manage VMs locally is using
Vagrant. [Install it](https://www.vagrantup.com/) and start a VM
loaded with Ubuntu 14 by running the command `vagrant init
sincerely/trusty64`. SSH into it with `vagrant ssh`, do an `ls` to
make sure everything is working. All right, that was the easy
part. Vagrant initializes the virtual machine with a default unsafe
SSH key. In order to access this VM as root, you have to copy your own
SSH key into this VM, and add it to the authorized keys of the root
account. Assuming that the key you want to copy is in
`/Path/to/your/id_rsa.pub`, run the following command:

    scp -P 2222  /Path/to/your/id_rsa.pub vagrant@127.0.0.1:/tmp

If you are prompted for a password, enter `vagrant`, the default
password for the default Vagrant box. Now SSH into the machine again
with `vagrant ssh` from within the directory where it was created, and
run the following commands in order to add your key to the root
account's authorized keys:

    sudo su
    mkdir -p -m 700 /root/.ssh
    cat /tmp/id_rsa.pub >> /root/.ssh/authorized_keys
    chmod 600 /root/.ssh/authorized_keys

Now you should be able to SSH from anywhere on the host computer into
the VM as root with `ssh -p 2222 root@127.0.0.1`. The default Vagrant
box comes with the user `vagrant` that has sudo rights, and one could
run most of the commands we will use for demo purposes with that
user. The aim of adding the root user is to make the examples uniform.

Last but not least here is what the contents of the inventory file
should be:

    server ansible_ssh_port=2222 ansible_ssh_host=127.0.0.1

### <a name="digitalocean"></a>DigitalOcean

The easiest way to create a DigitalOcean "droplet" is to use their web
interface. If you do so, don't forget to add your SSH key. It's the
last box at the bottom of the form before the "Create Droplet"
button. Just copy the contents of `~/.ssh/id_rsa.pub` or wherever you
have your SSH key and paste it in there.

In case you want to create and remove droplets liberally, and if you
are among the chosen few who can get a Python script with dependencies
working, you can use the `droplets.py` in this repo to create, list or
delete new DigitalOcean droplets. This script will create the droplet
with your SSH key already included, which will save you one more
step. Keep in mind that the initialization of a droplet will take a
few minutes, which means that you can't access a droplet right after
creating it. You can find out whether a droplet is ready for use by
running `python droplet.py list`. An active droplet will be listed as
having status `active`.

### Failing connection on server change

A confusing situation that frequently occurs when you recreate a local
VM, or wipe a server clean without changing its IP address, is that
Ansible (or simply SSH, for that matter) fails to connect, because the
fingerprint of the server changed. This issue is easy to
alleviate. Open the file `~/.ssh/known_hosts`, find the line that
starts with the IP address you are trying to connect to (and possibly
also contains the port, if it's non-default, in the
`[IP_ADDRESS]:PORT` format), and delete it.

### Ping it

Once you have your test server set up, run the following command to
check whether Ansible can contact the server:

    ansible -i inventory server -m ping

As a response, you should see the following, anything else means
something went wrong:

    server | success >> {
        "changed": false,
        "ping": "pong"
    }

You're right, the above command is too much stuff for a simple
ping. The stand-alone `ansible` command is rarely used, though; it is
mostly for the purpose of testing individual modules, or running
emergency commands on a set of servers. The above ping command does
the following: Use the inventory passed with the `-i` argument to run
the module passed with the `-m` argument. The concept of modules will
be explained in the next section. The ping module does not need any
arguments, but if it did, it would have been possible to pass them
with another switch. But as mentioned, we are interested in more
complicated stuff and not a crappy replacement for `ssh -c`, so read
on for plays, roles, and more.

## Plays, Modules, etc

There are only four fundamental concepts necessary for grokking
Ansible; if you understand these, you're halfway there. To make it as
simple as possible, here is a plain list:

* **Modules** are units of action. For pretty much everything you
    would do on a server, there is a module. They can be built-in or
    add-ons. Examples are ping, copy/modify/delete file, install
    packages, start/stop/restart a service etc.

* **Inventory** is the specification of a set of servers and how to
    connect to them. Ansible provides very convenient ways to specify
    sets of servers, and aliases for these.

* **Roles** are collections of actions that serve a purpose, and data
    that belongs to these actions. Examples are installing,
    configuring and then starting a database server, or retrieving
    code, building it, moving it to servers and runing it.

* **Playbooks** are collections of roles to run on a cluster of
    servers, completed with more data.

So in effect, **roles are collections of module applications, and
playbooks are specifications of which roles should be matched to which
inventory**. Module application means that a module is ran on a host
with some arguments.

## Writing plays & roles

Let's get going with roles, then. The example I want to cover here is
the average case of an RDBMS-driven website running on Python. What do
we need on this server? Well, first of all, we need to forbid root SSH
access, and create an admin user with sudo rights who is allowed to do
rooty stuff instead. The gods of sysadministan have agreed that this
is the right thing to do; who are we to contest that?  Not that it
sinks your server's chances of getting hacked, but I don't want to be
the one responsible if it happens.

Here is a simple playbook that achieves this:

```yml
- hosts: server
  remote_user: root
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

This playbook runs on `server` (as specified by `hosts`) as user
`root` (as specified by `remote_user`). The list of tasks are executed
as Ansible modules. The admini user is created, given sudo rights, the
user's SSH key is copied for admini, and finally, SSH login as root is
deactivated.

You're probably asking yourself about the format. It's YAML, yet
another markup language. The good things about it: it's neither XML
nor JSON. The bad thing: It's a markup language, and sometimes you
have to bend over backwards to get what the crappiest programming
language would get done in two lines of code. That's the way Ansible
rolls, though, so you'll have to deal with it. In this simple example,
we are listing the tasks within the playbook, which should be OK for a
small provisioning exercise, but it should be obvious that as the
number of tasks grows, and the inventory specification gets more
complicated, this method will not work. Each task has a name, which is
more like a description, and a specification on the next line. The
specification starts with the name of a module, and continues with
parameters as fields. [This list of all available ansible
modules](http://docs.ansible.com/list_of_all_modules.html) should
leave no doubts that nearly every need can be served out of the box.

In order to run the above playbook, save it in a file named
`user_accounts.yml` next to the inventory. Or just navigate to the
`example` directory in this repo. Then run the following command:

    ansible-playbook -i inventory part1/user_accounts.yml

The reason we are running this playbook in the parent directory of the
playbook is that the `ansible.cfg` file which makes sure that we are
connecting as the right user is in there. The `ansible-playbook`
command runs playbooks instead of single modules, and is where the
real Ansible magic lies, so we'll be using it much more often. When
you run the above command, you should see a list of the tasks by name,
followed by information on whether anything changed, and a final line
that recaps this information. Here is what you should see when you run
`playbook_simple.yml` for the first time on a fresh server:

    PLAY RECAP **********************************************************
    server           : ok=5    changed=4    unreachable=0    failed=0

This output will look a bit more bowine if you have the `cowsay`
command installed, by the way. Among the 4 tasks we had in our
playbook, all have been executed, and led to changes in the system,
thus the entry `changed=4`. If we run the same playbook once more,
however, here is what we see:

    PLAY RECAP ************************************************************
    server             : ok=5    changed=0    unreachable=0    failed=0

Now, `changed=0`, because the tasks do not have to be run, as they
would not lead to any changes in the system. This is what is meant
with *idempotent*; re-running this playbook (and ideally any playbook)
will not lead to a different system, no matter how many times you've
already run it.

## Who is Ansible on my server?

One thing that is relatively confusing with Ansible is who the hell
you actually are on a server. There are a number of different
configuration options, command line switches, and playbook options
that have an effect on the user Ansible runs the actions under. Here
is a tiny playbook that we will use to print the Ansible user (can be
found in `example/part1/whoami.yml`):

```yml
- hosts: server
  remote_user: admini
  tasks:
    - name: Print the actual user
      command: whoami
```

In order to see the output of the `whoami` command, you have to run
the playbook command with the next level of verbosity:

    ansible-playbook -i inventory part1/whoami.py -v

Here is the output we should see when we run this playbook on the
server that we provisioned with `playbook_simple.py`:

```
# bla bla bla....
TASK: [Print the actual user] *************************************************
changed: [server] => {"changed": true, "cmd": ["whoami"], "delta": "0:00:00.002952", "end": "2015-03-21 20:54:58.971190", "rc": 0, "start": "2015-03-21 20:54:58.968238", "stderr": "", "stdout": "admini"}

# a little more bla bla
```

So the `remote_user` instruction works; we are in fact `admini` on the
server. But what if we wanted to run a command that requires sudo? In
that case, we simply add the `sudo: yes` option, with the playbook
now looking like this:

```yml
- hosts: server
  remote_user: admini
  sudo: yes
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

Supplying the user in each and every playbook can be cumbersome and
error-prone if you have many of them, so Ansible offers an easy way to
set a default for all playbooks in a directory, by creating an
`ansible.cfg` file and putting the following in there:

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

**Aside on specifying booleans**: You can specify boolean values for
  tasks and plays using pretty much any truey or falsy value; all of
  these work: `yes, no, True, true, TRUE, false`. In this tutorial
  `yes` and `no` are preferred, because that's what I see in other
  playbooks most frequently.

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

With this playbook, we would get a web and a database server, and the
tools to check out our code. It would be rather messy if we continued
adding more tasks into this play, however, not to mention the
organization of configuration files and templates that will come up
later. Therefore, let's take the step mentioned earlier and separate
out our playbooks into roles. A **role** gathers tasks that are
conceptually coherent, and bundles them with some other things like
files, templates and triggers. Roles reside in the `roles` directory
next to playbooks, and have the following file structure:

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
that can be rendered and copied to a server.

Let's move the tasks from the playbook that installed packages into a
role called `packages`, and use it in a new playbook. You can find the
playbook and the roles in the directory `example/part2`. As you can
see, the directory tree becomes rather convoluted even for the
simplest role-based organization, but again, this is how Ansible
rolls. Here is how `roles/packages/tasks/main.yml` looks:

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

This role, which installs the usual Debian packages a Python web
application needs, is relatively straightforward, with the exception
of a loop in the last task. The `with_items` option enables looping a
task over a list, and replacing `{{ item }}` with the elements of that
list. This is equivalent to repeating the task with the list
elements. The double curly braces is the syntax used by Jinja2 for
inserting variables.

## Variables

Variables in Ansible are what you would expect: placeholders for
values that might change according to circumstances. Using variables
is relatively straightforward; you can use them pretty much anywere by
wrapping the variable's name in double curly braces, such as the loop
that used `item` as a value above. This syntax for variable
substitution, taken over from Jinja2, can be used pretty much anywhere
in Ansible, but the more advanced uses of Jinja2 is restricted to
actual templates. In role and play definitions, only variable
substitution is allowed; it is not possible to use other Jinja2
features such as conditionals or looping.

Values for variables can be supplied through various mechanisms. In
the following, we will go through these, and go into detail where
necessary. For precedence of these different ways of defining
variables, see [the official
documentation](http://docs.ansible.com/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable).

##### In the inventory

Variables declared in the `var_name=var_value` format on inventory
elements are available in the tasks that run on these elements. An
example is the `ansible_ssh_host` and `ansible_port` we used above.

##### In a play

Variables can be defined in the `vars` section of a play, and can then
be used in any tasks that are part of that play.

##### As separate YML files

It is possible to include arbitrary yaml files with variable
definitions using the `include_vars` module in a play.

##### As arguments to included tasks and roles

It is possible to pass arguments to included tasks and roles in
playbooks. We will not consider task includes here, since roles are a
better alternative, but you can [refer to the
documentation](http://docs.ansible.com/playbooks_roles.html#task-include-files-and-encouraging-reuse)
if you feel like it. Passing arguments to roles works with the
following syntax:

```yml
- hosts: server
  roles:
    - packages
    - { role: db, password: 'notapassword' }
```

##### From the command line

You can use the command line switches `--extra-vars` or `-e`, followed
by a comma-separated list of variables in `var_name=var_value`
format. These variables have the highest precedence.

##### Registered from a task

This very useful feature allows you to store the result of a task in a
variable and use it in following tasks. Here is a toy example of a
playbook that does this:

```yml
- hosts: server
  tasks:

    - name: Task one
      command: shuf -i1-100 -n1
      register: whatisit

    - name: Task two
      command: echo {{ whatisit }}

    - name: Task three
      command: echo "blah"
      when: whatisit.changed
```

The output of the first task (a random number) will be saved in the
variable `whatisit`, and then printed by the second task. You have to
run the above playbook, which you can find in
`example/part2/save_var.yml`, with higher verbosity to see the output
of the second task:

    ansible-playbook -i inventory part2/save_var.yml -vv

The output of the second task might be a but surprising; it's a
dictionary with various bits of information on the first task. Among
the useful entries are `changed`, which points to whether any changes
happened, and `rc` which stands for return code. You can use these
variables to steer following tasks by referring to them using dot
syntax, such as `whatisit.changed`. This is what happens in the third
task above, which is run only when the first task has changed, that is
always, since it's a command.

##### Facts gathered by Ansible

Ansible gathers a ton of information on the hosts on which it runs for
its own use. This information is made available in the playbooks, too.

##### Hostvars and groupvars

These offer one of the most versatile means of supplying variables in
Ansible. Hostvars are simple: You can put the variables for a single
host named e.g. `server` in the file `host_vars/server` instead of
cluttering the inventory. These variables will then be loaded, and
available for tasks running on this host. Group vars are connected to
inventory groups. You can gather individual hosts under groups in the
inventory by prefixing them in a group name in brackets, as in the
following sample inventory file:

```
[db_servers]
db_server_1
db_server_2
```

Any playbooks can then use the group name instead of individual host
names as `hosts`. The `group_vars` feature is very similar in this
respect to the `host_vars` one: a variables file in the directory
`group_vars/db_servers` will be available to the hosts in the
`db_servers` group. There is one special group: `all`, in which all
hosts are included. Consequently, the variables in the file
`group_vars/all` are available on all hosts.

In the example orchestration infrastructure we are building, we would
like to have the ability to deploy different web applications,
preferably by supplying the name of the project on the command line
instead of editing a file. This can be achieved by using command line
variables. The correct sets of variables can be loaded by storing
application-specific variables in separate files and including these
based on the name of the application. Common variables would go into
the `group_vars/all` file. The playbook
`example/part2/deploy_app.yml`, which builds and runs a single web
application, uses these methods to load data. Here are the contents of
this playbook:

```yml
- hosts: server
  pre_tasks:
    - name: Load passwords
      include_vars: "vars/passwords.yml"
  roles:
    - packages
    - db

- hosts: server
  pre_tasks:
    - name: Load variables
      include_vars: "vars/{{ app }}"
  roles:
    - code
    - build
    - nginx
```

We are using the `include_vars` module to load variables files
dynamically. In the first play, `include_vars` is used to load the
`passwords.yml` file that contains the database password. This file is
encrypted; dealing with passwords in encrypted files will be explained
in the next section. The second playbook loads the file that contains
the variables belonging to the application specified by `app`. As you
can see in this second `include_vars`, variables can be subsituted in
many places where you would need them. What's peculiar in this
playbook is the use of `pre_tasks` in both plays. In a play, the order
of execution is first roles and then tasks. The tasks listed in
`pre_tasks`, on the other hand, are executed before the roles. In this
case, the variables loaded through the `include_vars` calls in
`pre_tasks` make the variables in those files available to the rest of
not only this play, but the rest of the playbook. Assuming that we
want to deploy the application facetweet from the `example/websites`
directory, here is how the Ansible command would look like:

    ansible-playbook -i inventory part2/deploy_app.yml -e "app=facetweet" --ask-vault-pass

## Handlers

Let's move on to the second role in the first play above. The `db`
role does two things: copy an alternative Postgres authentication
configuration file (`pg_hba.conf`) onto the server, creating a
time-stamped backup if it differs, and adding a new admini user. The
first of these two actions requires a restart of the Postgres
server. We could add this as a manual step after the configuration
file is copied over, but a better idea is to have a handler that is
triggered whenever an action requiring a restart of the Postgres
server is executed. Such triggers go into the `handlers/main.yml` file
in a role directory, and should have the following format:

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
the service will be restarted only once, at the end of the play,
instead of with each configuration change.

## Vault

The password file that is included with `include_vars` in the playbook
`deploy_app.yml` is encoded using a built-in Ansible feature named
Vault.  Vault is extremely easy to use, as witnessed by the [brevity
of the official
documentation](http://docs.ansible.com/playbooks_vault.html). You can
create an encoded file that contains variables using the following
command:

    ansible-vault create password.yml

You will be prompted for a password that will be used to encode the
file, and then dropped into the editor specified by the `EDITOR`
environment variable (most probably vi or vim if you didn't set it
somewhere). You can edit or rekey (i.e. change the password for) this
file using the associated options, or encrypt existing files. The
really useful functionality is running playbooks that refer to
encrypted files without having to decrypt them first. To do this, you
have to pass the argument `--ask-vault-pass` to `ansible-playbook`,
which will take care of the rest. The password for the `passwords.yml`
included in the examples is `testtest`, by the way.

## Tasks & Modules

Ansible has a lot of built-in modules, covering every step of our goal
of deploying a Python web application. The roles in the second play of
`deploy_app.yml`, namely `code`, `build` and `nginx` use these modules
combined with a number of other techniques. We will go through these
now.

The `code` role in `code/tasks/main.yml` has two tasks and is
responsible for checking out the code for the demo websites from
Github. The first task makes sure that the github.com domain key is in
the `known_hosts` file of the Ansible user using the `lineinfile`
module. This module will make sure that a line is there or not,
depending on the `state` argument. If the `regexp` argument is also
provided, it will be used to find the line that should be replaced in
case of `state=present`, or removed for `state=absent`. This task uses
two other features. One is the use of `ansible_ssh_user` in the path
specification for the `known_hosts` file; this variable is one of
those provided by Ansible itself. The other is the use of the
**lookup** plugin. This plugin enables reading data from the local
system, either by piping the result of a command, as in this case, or
by reading a file. By looking up the github.com key locally, and
copying it onto the target server, we can be sure that we're using the
right key, and can securely clone the repo. The second task in
`code/tasks/main.yml` uses the `git` module, and is relatively
straightforward: It makes sure that the repo is cloned, and by default
updates to head of master. The `lookup` module is used again, to get
the remote origin of this repo, to avoid harcoding it.

The second role, `build`, uses some of the most popular Ansible
modules to create a virtualenv, install the code, and populate the
database. The `file` module has a lot of options, and can be used for
various different purposes, such as removing a file, linking two
files, changing file permissions, or creating a directory. You could
even say it does too much, but it does the work. This module is used
twice, to create the directory in which the virtualenvs will reside,
and the directory for log files. The virtualenv itself is created by
the `pip` module, which gets the path of the virtualenv as an option,
and the name of the dependency file. The values for all these options
come from the variables file `vars/facetweet`. If you inspect that
file, you will see that the values are composed from each other. That
is, a variable can refer to another one coming before it in its value,
as in the following few lines:

```yml
home_dir: /home/admini/
code_dir: "{{ home_dir }}code/example/websites/facetweet/"
venv_base_dir: "{{ home_dir }}venvs/"
venv: "{{ venv_base_dir }}facetweet"
```

This is a really useful feature that allows one to create complicated
configuration files without repetition.

After installing the dependencies and the application, the `build`
role creates the application configuration using the `template`
module. This module can render Jinja2 templates using all the
variables that are provided with the different methods listed
above. In this case, the application configuration is generated using
mostly the variables in the loaded `vars/{{ app }}` file. The same
module is also used to create the upstart configuration file.

**YAML Note**: Some lines that have variable insertion with the `{{
}}`syntax are quoted (such as the `command` line of the `Install {{
app }}` task), and some aren't. The reason for this difference is that
when a line starts with curly braces, it has to be quoted, so that
it's not parsed as a YAML dictionary, but a line for Ansible
processing instead. See [the
documentation](http://docs.ansible.com/playbooks_variables.html#hey-wait-a-yaml-gotcha)
for more details.

Next comes the creation of a database for the app using the
`postgresql_db` module. The database name is looked up from the vars
file, while the password is looked up from the encoded passwords
file. The result of this task is registered in the variable
`db_created` to check whether it was changed in the next task. If it
changed, i.e. if a new database was created, the command from the web
application to create the tables from the SQLAlchemy schema is
called. The aptly named `command` module is run to call this
command. The option `environment` is used set values in the
environment in which the command is run, passing the configuration
file generated earlier as `APP_CONFIG` to be used by application code.

Once all these tasks have been executed with the command mentioned
above and run to completion, the web application can be accessed on
the server. If you deployed to a VM with Vagrant, edit the
Vagrantfile, and uncomment the following line to match port 80 of the
guest (the VM) to port 8080 on your host machine:

    config.vm.network "forwarded_port", guest: 80, host: 8080

Don't forget to reboot the VM with `vagrant reload`. Afterwards, the
application you deployed (one of facetweet or hackerit) should be
available on http://localhost:8080. If you are deploying to an
external server, such as DigitalOcean as explained above, you can also
update your `/etc/hosts` file (or `/private/etc/hosts` if you're on a
Mac), adding the lines `IP.ADDRESS hackerit.com` and `IP.ADDRESS
facetweet.com`, where `IP.ADDRESS` is replaced with the IP-address of
your server. Afterwards, if you go to hackerit.com on your browser,
you should see the login page of the hackerit app.

### Tags

What if you want to run tasks in a playbook or role only selectively,
dependent on a command line option? Your Ansible playbook might
include tasks that you want to repeat regularly and independent of the
rest, such as changing the configuration of a service and restarting
it, or backing up log files. Ansible offers tags for tasks to
accommodate this use case. Task definitions accept a `tags` option,
and the `ansible-playbook` command can be given a list of tags as
argument. With a tag list specified, Ansible runs only those tasks
that have one of the given tags. The playbook
`example/part2/db_tasks.yml` uses tags to switch between making a
backup of an application database and restoring this backup. This
playbook includes a single role that runs the tasks for backing up the
table for the applications specified on the command line. The roles
have either the `backup_db` or the `restore_db` tag, only the first
task that creates the directory for saving dumps having both. If we
wanted to dump the database for facetweet, for example, we would need
to run the following command:

    ansible-playbook -i inventory part2/db_tasks.yml -e "app=facetweet" -t restore_db --ask-vault-pass

With this command, only the tasks containing the `restore_db` tag from
the `db_tasks.yml` playbook and `db_maintenance` role will be run. One
strange thing is that the `pre_tasks` jobs that we use to load
variables and passwords also have to be tagged; otherwise, they are
not included in tagged playbook runs. After the variables are loaded,
the directories in which the dumps will be saved on the server and
copied locally are created. The local directory is created with the
`delegate_to` option, a feature that allows communication between
hosts. Here we are using it to avoid splitting a single-task role just
to change the host. On the server, the database is dumped into a file
that has the same name as the app with the `pg_dump` command. For this
task, we need to use the `shell` module, because the `command` module
does not allow shell functionality such as piping the output of a
command into a file. The dump is then copied into the local dumps
directory created earlier with the `fetch` module. Restoring the
database is the same process in reverse: Copy the file from the same
location with `copy`, reset the application database, and then restore
the dump.

## Combining roles, plays and playbooks

What if we wanted to write a playbook that provisions a server from a
clean install and installs both applications, restoring from a
database in the process if the file is available? This playbook would
not take any arguments, and would run through until both application
processes were running and online. The include mechanism of Ansible is
very useful in such situations where we want to create a complete
playbook from smaller parts, achieving a certain level of
abstraction. The play `part2/site.yml` does not contain any plays
itself, but includes other playbooks to bring together various
components of the application server:

```yml
- hosts: server
  tasks:
    - name: Load passwords
      include_vars: "vars/passwords.yml"

- include: provision.yml
- include: app.yml app=facetweet
- include: app.yml app=hackerit

- hosts: server
  roles:
    - { role: db_restore, app: 'facetweet' }
    - { role: db_restore, app: 'hackerit' }
```

This playbook is essentially a splitting of the `deploy_app.yml`
playbook above, along with a new role `db_restore` that restores an
app database. The passwords are loaded now with a single task at the
very beginning, and the roles that install the necessary packages and
configure the database are in the playbook `provision.yml` that is
imported into this playbook with an include directive. There is also a
separate playbook for installing one web application, and this
playbook is imported twice with the app variable set differently in
each. The reason there is a new role for restoring the database,
instead of using the existing `db_maintenance` role, is that the
existing role uses tags to flip between dumping and restoring a
database. It is not possible to set tags within playbooks, however,
which means that we cannot force the restoring of a database without a
command-line switch.

If we were to add a new web application to our server, we would add it
to `site.yml` along with the variables files in `vars`, and our
deployment infrastructure would be ready to go.
