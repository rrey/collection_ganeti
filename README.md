# Ansible Collection - rrey.ganeti


This collection includes a variety of Ansible content around [Ganeti](https://ganeti.org/)

## Included content

Click on the name of a plugin or module to view that content's documentation:

  - **Modules**:
    - ganeti_instance
  - **playbooks**
    - create_or_destroy_vm.yml (demo purpose only)
  - **roles**
    - fix_vm_setup (demo purpose only)
    - ganeti


## Using this collection

Create an inventory such as:

```
# inv.ini
test-rre.psvm
```

and group_vars with following minimal information (example):

```
# group_vars/all
---

ganeti_address: ganeti_rapi_server_address
ganeti_credentials:
  user: some_user_on_ganeti
  password: some_secret_password

ganeti_vm_create:
- name: test-rre.psvm
  memory: 2048
  vcpu: 2
  disks:
  - name: root
    size: 20G
  node: ivc-06
  os_type: image+centos-8
```

Install the collection:

```
ansible-galaxy collection install rrey.ganeti
```

Call the playbook for the demo with your inventory:

```
ansible-playbook rrey.ganeti.create_or_destroy_vm -i ./inv.ini
```
