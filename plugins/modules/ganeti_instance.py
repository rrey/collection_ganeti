#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020 Stefan Valouch (svalouch), <svalouch@valouch.com>
# BSD 3-Clause License

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: ganeti_instance
short_description: Manage Ganeti instances
description:
  - Manage instances supervised by a Ganeti cluster
  - Instances can be started, stopped and restarted
  - Allows semi-complex creation of instances
author: Stefan Valouch (@svalouch)
requirements:
  - "python >= 3.5"
  - "ganeti >= 2.16"
  - requests
options:
    address:
        description:
          - Address the RAPI listens to
        required: false
        default: localhost
        type: str
    port:
        description:
          - RAPI port
        required: false
        default: 5080
        type: int
    user:
        description:
          - Name of the user that connects to RAPI
        required: false
        default: None
        type: str
    password:
        description:
          - Password associated with the user account
        required: false
        type: str
    job_timeout:
        description:
          - If ``wait`` is `true`, specifies the maximum amount of time in
            seconds to wait for the job to finish before moving on
        required: false
        type: int
        default: 300
    state:
        description:
          - Desired state of the instance.
          - States except ``absent`` and ``present`` report an error if the
            instance does not exist.
          - ``present`` creates the instance.
          - ``absent`` deletes the instance.
        required: true
        choices:
          - absent
          - present
          - restarted
          - started
          - stopped
    wait:
        description:
          - If ``true``, waits for the job that gets submitted to ganeti by
            the module.
          - The module waits for ``job_timeout`` seconds before reporting an
            error.
          - If ``false`` the module submits the job and returns immediately
            instead of waiting for ganeti to finish the job. There is no way
            for the module to detect if the job results in an error.
        required: false
        type: bool
        default: true
    disk_template:
        description:
          - If ``state`` is ``present``, specifies the disk template to use.
          - If ``ext`` is specified, the ``provider`` needs to be specified in
            the ``disks`` structure.
          - Templates not enabled on the cluster will result in an error.
        type: str
        choices:
          - sharedfile
          - diskless
          - plain
          - gluster
          - blockdev
          - drbd
          - ext
          - file
          - rbd
        default: plain
    disks:
        description:
          - Specifies the disks and their options in a list.
        type: list
        suboptions:
            size:
                description:
                  - Size of the disk in megabytes
                type: int
                required: true
            mode:
                description:
                  - Disk access mode, such as ``rw``
                type: str
            name:
                description:
                  - Name of the disk
                  - This is optional for some templates/providers, but may be
                    used by the os creation script.
                type: str
            provider:
                description:
                  - `extstorage` provider, required if ``disk_template`` is
                    set to ``ext``.
                type: str
    nics:
        description:
          - Specifies the network interfaces for the instance.
          - The ``mode`` defines which of the suboptions are required, refer
            to the Ganeti documentation in instance creation.
        type: list
        suboptions:
            bridge:
                description:
                  - The name of the bridge to use
                  - Used with ``mode`` set to `bridged`
                type: str
            name:
                description:
                  - Name of the network interface.
                  - This is optional but may be used by the os creation script
                    and helps when working with gnt-instance.
                type: str
            ip:
                description:
                  - IP that should be assigned to the interface.
                  - This may be used by os creation scripts or drivers, and is
                    usually optional.
                type: str
            vlan:
                description:
                  - VLAN ID to use
                  - Optional
                type: int
            mac:
                description:
                  - Overwrite the MAC of this interface
                  - Optional, by default the cluster-wide MAC-prefix is used
                    to compute a unique MAC address
            link:
                description:
                  - Interface on the host this virtual interface is connected to.
                  - Example: Specify the name of the bridge to connect the tap
                    device to.
                type: str
            mode:
                description:
                  - Operation mode.
                type: str
                choices:
                  - routed
                  - bridged
                  - openvswitch
                required: true
            network:
                description:
                  - Network this interface is connected to
                type: str
    hypervisor:
        description:
          - Overwrite the default hypervisor setting set in the cluster.
          - Only enabled hypervisors can be chosen, specifying a disabled one
            results in an error.
        type: str
        choices:
          - chroot
          - xen-pvm
          - kvm
          - xen-hvm
          - lxc
          - fake
    iallocator:
        description:
          - IAllocator to use
        type: str
        default: hail
    name:
        description:
          - Name of the instance
        required: true
        type: str
    os_type:
        description:
          - Name of the OS create script and variant to deploy
          - The availability depends on the cluster setup
        type: str
    osparams:
        description:
          - Optional parameters that are passed to the os create script.
          - Specify flat ``key: value`` pairs
        type: dict
    pnode:
        description:
          - Name or address of the primary node
          - If not given, the node running RAPI will be used
        type: str
    snode:
        description:
          - Name or address of the optional secondary node.
          - If set, ``pnode`` has to be set.
        type: str
    memory:
        description:
          - Amount of memory in megabytes to allocate to the instance
        type: int
    vcpus:
        description:
          - Number of vCPUs to give to the instance
          - If not given, the clusters defaults are used.
        type: int
'''

EXAMPLES = r'''
---
- name: start instance
  ganeti_instance:
      user: ansible
      password: supersecret
      name: vmname
      state: started

- name: stop instance
  ganeti_instance:
      user: operator
      password: operator
      name: vmname
      state: stopped

- name: restart instance
  ganeti_instance:
      user: root
      password: toor
      name: vmname
      state: restarted

- name: create a new instance
  ganeti_instance:
      address: ganeti.example.com
      user: admin
      password: bofh
      name: vmname
      state: present
      memory: 512
      vcpus: 1
      disk_template: plain
      disks:
        - name: root
          size: 10G
      nics:
        - mode: bridged
          link: br0
      os_type: debian+default
'''

RETURN = r'''
changed:
    description: Whether the the module performed a change related to the instance.
    type: bool
message:
    description: Optional message returned as a result of an action.
    type: str
    sample: Instance created
'''

# TODO return the job_id

from ansible.module_utils.basic import AnsibleModule
import requests
import time


def query(module, method='GET', resource=None, data=None):
    '''
    Queries the remote RAPI.

    :param module: The AnsibleModule that invokes the function. It uses
        `address``, ``port``, and optionally ``user``/``password`` attributes.
    :param method: The HTTP verb to use (DELETE, GET, POST, PUT).
    :param resource: If set, gets appended to the url to query a specific
        resource.
    :param data: Optional dict of data to send in the body of the query.
    :return: The ``requests.Response``.
    '''
    meth = method.upper()
    if meth not in ('DELETE', 'GET', 'POST', 'PUT'):
        module.fail_json(name=module.params['name'], message='Invalid HTTP verb')

    url = 'https://{0}:{1}/2'.format(module.params['address'], module.params['port'])

    auth = None
    if module.params['user'] != '' and module.params['password'] != '':
        auth = (module.params['user'], module.params['password'])

    headers = {'Content-Type': 'application/json'}

    if resource is not None and len(resource) > 0:
        url += resource

    return requests.request(method=meth, url=url, headers=headers, json=data,
                            auth=auth, verify=False)


def instance_create(module):
    params = {
        '__version__': 1,
        'beparams': {
            'memory': module.params['memory'],
            'vcpus': module.params['vcpus'],
        },
        'disk_template': module.params['disk_template'],
        'hypervisor': module.params['hypervisor'],
        #'iallocator': module.params['iallocator'],
        'instance_name': module.params['name'],
        'os_type': module.params['os_type'] if module.params['os_type'] is not None else 'debootstrap+default',
        'pnode': module.params['pnode'],
        'snode': module.params['snode'],
        'mode': 'create',
    }

    # disks
    DISK_PARAMETERS = ['size', 'mode', 'name', 'provider']
    disks = []
    disk_i = 0
    for disk in module.params['disks']:
        disk_params = dict()
        if 'size' not in disk.keys():
            module.fail_json(name=module.params['name'], msg='No "size" given for disk #{0}'.format(disk_i))
        elif 'provider' in disk.keys() and disk['provider'] == 'ext':
            # things outside DISK_PARAMETERS are now appended as kwargs
            for key in disk.keys():
                disk_params[key] = disk[key]
        else:
            for key in disk.keys():
                if key in DISK_PARAMETERS:
                    disk_params[key] = disk[key]
                else:
                    module.fail_json(name=module.params['name'], msg='Invalid disk parameter for disk #{0}: {1} is not a valid key'.format(disk_i, key))
        if len(disk_params) != 0:
            disks.append(disk_params)
            disk_i += 1
    if len(disks) > 0:
        params['disks'] = disks

    # nics
    nics = []
    nic_i = 0
    for nic in module.params['nics']:
        nic_params = dict()
        for key in nic.keys():
            if key not in ['bridge', 'name', 'ip', 'vlan', 'mac', 'link', 'mode', 'network']:
                module.fail_json(name=module.params['name'], msg='Invalid nic parameter for nic #{0}: {1} is not a valid key'.format(nic_i, key))
            else:
                if key == 'mode' and nic[key] not in ['routed', 'bridged', 'openvswitch']:
                    module.fail_json(name=module.params['name'], msg='Invalid mode {1} for nic {0}'.format(nic_i, nic[key]))
                    return
                nic_params[key] = nic[key]

        if len(nic_params) != 0:
            nics.append(nic_params)
            nic_i += 1
    if len(nics) > 0:
        params['nics'] = nics

    # osparams
    if len(module.params['osparams']) > 0:
        osparams = dict()
        for k, v in module.params['osparams'].items():
            if isinstance(v, dict) or isinstance(v, list):
                module.fail_json(name=module.params['name'], msg='Got complex type for osparams key %s' % k)
            osparams[k] = v
        if len(osparams) > 0:
            params['osparams'] = osparams

    response = query(module=module, method='POST', resource='/instances', data=params)
    if response.status_code != 200:
        module.fail_json(name=module.params['name'], msg='API call failed with code {0}: {1}'.format(response.status_code, str(response.text)))
    else:
        j_id = int(response.text)
        if module.params['wait']:
            (success, message) = wait_for_job(module, j_id)
            if not success:
                module.fail_json(name=module.params['name'], msg=message)
            else:
                return (True, 'Instance {0} created'.format(module.params['name']))
        else:
            return (True, 'Create job added')
    return (False, 'An error occured')  # fail_json does not terminate in unit testing


def instance_start(module):
    '''
    Starts the instance.
    '''
    response = query(module=module, method='PUT', resource='/instances/{0}/startup'.format(module.params['name']))
    if response.status_code != 200:
        module.fail_json(name=module.params['name'], msg='API call failed with code {0}: {1}'.format(response.status_code, str(response.text)))
    else:
        j_id = int(response.text)
        if module.params['wait']:
            success, message = wait_for_job(module, j_id)
            if not success:
                module.fail_json(name=module.params['name'], msg='Stop action failed: {0}'.format(message))
            else:
                return (True, 'Startup complete')
        else:
            return (True, 'Startup signal sent')


def instance_stop(module):
    '''
    Stops the instance.
    '''
    response = query(module=module, method='PUT', resource='/instances/{0}/shutdown'.format(module.params['name']))
    if response.status_code != 200:
        module.fail_json(name=module.params['name'], msg='API call failed with code {0}: {1}'.format(response.status_code, str(response.text)))
    else:
        j_id = int(response.text)
        if module.params['wait']:
            success, message = wait_for_job(module, j_id)
            if not success:
                module.fail_json(name=module.params['name'], msg='Stop action failed: {0}'.format(message))
            else:
                return (True, 'Shutdown complete')
        else:
            return (True, 'Shutdown signal sent')


def instance_destroy(module):
    '''
    Destroys the instance. This cannot be undone.
    '''
    response = query(module=module, method='DELETE', resource='/instances/{0}'.format(module.params['name']))
    if response.status_code != 200:
        module.fail_json(name=module.params['name'], msg='API call failed with code {0}: {1}'.format(response.status_code, str(response.text)))
    else:
        j_id = int(response.text)
        if module.params['wait']:
            success, message = wait_for_job(module, j_id)
            if not success:
                module.fail_json(name=module.params['name'], msg='Restart action failed: {0}'.format(message))
            else:
                return (True, 'Destruction complete')
        else:
            return (True, 'Destruction signal sent')


def instance_restart(module):
    '''
    Restarts an instance.
    '''
    response = query(module=module, method='POST', resource='/instances/{0}/reboot'.format(module.params['name']))
    if response.status_code != 200:
        module.fail_json(name=module.params['name'], msg='API call failed with code {0}: {1}'.format(response.status_code, str(response.text)))
    else:
        j_id = int(response.text)
        if module.params['wait']:
            success, message = wait_for_job(module, j_id)
            if not success:
                module.fail_json(name=module.params['name'], msg='Destroy action failed: {0}'.format(message))
            else:
                return (True, 'Destruction complete')
        else:
            return (True, 'Shutdown signal sent')


def wait_for_job(module, job_id):
    '''
    Waits for a job, for at most ``module.job_timeout`` seconds.
    '''
    ts_start = time.time()
    status = ''
    while True:
        response = query(module=module, method='GET', resource='/jobs/{0}'.format(job_id))
        if response.status_code != 200:
            return (False, 'Error waiting for job {0}, response code {1}'.format(job_id, response.status_code))
        else:
            js = response.json()
            status = js['status']
            if status not in ['canceled', 'error', 'success']:
                if ts_start + module.params['job_timeout'] < time.time():
                    return (False, 'Timeout waiting for job {0}, ts_start {1} timeout {2} time.time() {3}'.format(job_id, ts_start, module.params['job_timeout'], time.time()))
            else:
                if status != 'success':
                    if 'opresult' in js and len(js['opresult']) > 0:
                        # get the first message only
                        msg = 'Job {0} failed: {1}'.format(job_id, js['opresult'][0][1])
                    else:
                        msg = 'Job {0} failed with status "{1}"'.format(job_id, status)
                    return (False, msg)
                else:
                    return (True, 'Success')
            time.sleep(2)


def run_module():
    # list of possible values for disk_template, taken from rapi docs v2.16
    disk_templates = ['sharedfile', 'diskless', 'plain', 'gluster', 'blockdev',
                      'drbd', 'ext', 'file', 'rbd']
    hypervisor_choices = ['chroot', 'xen-pvm', 'kvm', 'xen-hvm', 'lxc', 'fake']
    state_choices = ['present', 'absent', 'restarted', 'started', 'stopped']

    module_args = dict(
        address=dict(type='str', default='localhost'),
        port=dict(type='int', required=False, default=5080),
        user=dict(type='str', required=False, default=None),
        password=dict(type='str', required=False, default=None, no_log=True),
        job_timeout=dict(type='int', required=False, default=5*60),
        state=dict(type='str', default='present', choices=state_choices),
        wait=dict(type='bool', default=True),  # wait for job completion

        # parameters for vm creation / modification
        disk_template=dict(type='str', default='plain', choices=disk_templates),
        disks=dict(type='list', required=False),
        hypervisor=dict(type='str', default='kvm', choices=hypervisor_choices),
        iallocator=dict(type='str', required=False, default='hail'),
        name=dict(type='str', required=True, aliases=['instance_name']),
        nics=dict(type='list', required=False),
        os_type=dict(type='str', required=False),
        osparams=dict(type='dict', required=False, default={}),
        pnode=dict(type='str', required=False, default=None),
        snode=dict(type='str', required=False, default=None),

        # beparams
        memory=dict(type='int', required=False),
        vcpus=dict(type='int', required=False),

    )

    changed = False
    message = ''

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    try:
        response = query(module, resource='/instances/' + module.params['name'])
    except requests.HTTPError as e:
        module.fail_json(message=str(e))

    if response.status_code == 404:
        # no instance found
        if module.params['state'] == 'present':
            changed, message = instance_create(module)
        elif module.params['state'] in ('restarted', 'started', 'stopped'):
            module.fail_json(message='Instance {0} is not present, can\'t set to {1}'.format(module.params['name'], module.params['state']))
        else:
            message = 'No instance found'
    else:
        instance = response.json()
        if module.params['state'] == 'present':
            message = 'Instance present'
        elif module.params['state'] == 'stopped':
            if instance['status'] not in ('ADMIN_down', 'ERROR_down'):
                changed, message = instance_stop(module)
            else:
                message = 'Instance already stopped, status {0}'.format(instance['status'])
        elif module.params['state'] == 'started':
            if instance['status'] != 'running':
                changed, message = instance_start(module)
        elif module.params['state'] == 'restarted':
            if instance['status'] == 'running':
                changed, message = instance_restart(module)
            else:
                changed = instance_start(module)
        elif module.params['state'] == 'stopped':
            if instance['status'] == 'running':
                changed, message = instance_stop(module)
        elif module.params['state'] == 'absent':
            changed, message = instance_destroy(module)

    response = query(module, resource='/instances/' + module.params['name'])
    instance = response.json()
    result = dict(
        changed=changed,
        message=message,
        instance=instance,
    )

    module.exit_json(**result)


if __name__ == '__main__':
    run_module()
