"""
Script to create, list and delete digitalocean droplets. First,
go to the Apps & API section on your DigitalOcean profile
page. Create a token with read & write access, and copy it into
~/.digitalocean. Create a virtualenv, pip install
python-digitalocean, then python create_droplet.py
create|list|delete

"""

import sys, os
import digitalocean

USAGE = """
Usage:
python droplets.py create | delete | list
"""

def main():
    with open(os.path.expanduser('~/.digitalocean'), 'r') as token_file:
        token = token_file.read().strip()
    if len(sys.argv) < 2:
        print USAGE
        return
    command = sys.argv[1]
    if command == 'create':
        create_droplet(token)
    elif command == 'list':
        list_droplets(token)
    elif command == 'delete':
        delete_droplet(token)
    else:
        print USAGE

def format_droplet(droplet):
    return "%s (%s) : %s" % (
        droplet.name,
        droplet.status,
        droplet.ip_address
    )

def create_droplet(token):
    droplet_name = raw_input("Enter droplet name: ")
    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as ssh_file:
        ssh_key = ssh_file.read().strip()
    droplet = digitalocean.Droplet(
        token=token,
        name=droplet_name,
        region='ams1',
        image='ubuntu-14-04-x64',
        size_slug='512mb',
        backups=False,
        ssh_keys=[ssh_key])
    droplet.create()
    print "Created droplet %s" % (droplet_name,)

def list_droplets(token):
    manager = digitalocean.Manager(token=token)
    droplets = manager.get_all_droplets()
    for droplet in droplets:
        print format_droplet(droplet)

def delete_droplet(token):
    manager = digitalocean.Manager(token=token)
    droplets = manager.get_all_droplets()
    for index,droplet in enumerate(droplets):
        print "%d %s" % (index, format_droplet(droplet))
    index = int(raw_input("Enter index for droplet to delete: "))
    droplet = droplets[index]
    yes_no = raw_input("Are you sure you want to destroy %s? [y/N] " %
                       droplet.name)
    if yes_no in ['y', 'Y']:
        droplet.destroy()
        print "Droplet %s destroyed" % droplet.name

if __name__ == "__main__":
    main()
