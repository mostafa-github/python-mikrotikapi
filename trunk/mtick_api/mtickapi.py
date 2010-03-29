import re

import sshlib

"""
__ Add to specific position __
/ip firewall nat add place-before=*1 ....
---> place the rule newly added before id=1

__ Move __
/ip firewall nat move *15 *5 
---> move id=5 to before id=15

"""

class MikrotikController:
    """Mikrotik Controlling Class."""
    ip = None #ip address

    port = 22 #port to use for ssh

    username = "admin" #username for ssh

    password = "" #password for ssh
    
    def __init__(self, **kwargs):
        """Set instance antributes from the @kwargs dictionary"""
        for k, v in kwargs.items():
            setattr(self, k, v)
    

    def ssh_cmd(self, cmd):
        """Perform @cmd on remote machine in ssh shell and return output of it 
        as a string"""
        # set connection details
        server = self.ip
        username = self.username
        password = self.password

        # build the ssh connection
        s = sshlib.SSHClient(username = self.username,
                password = self.password,
                hostname = self.ip,
                port = self.port
                )

        # get data
        res = s.run(cmd)
        print cmd
        return res

    def load_entity_list(self, cmd):
        """Load list of items of section @cmd on MikroTik.
        
        e.g.: cmd = "/ip address" ; will load list of all ip addresses as text output
        """
        # uncomment the next line and commend out the next one if you need to use this api 
        # for mticks with routeros <3.0
        #control_str = ":foreach i in=[%s find] do=[:put [$i]\n :put [%s print terse from=$i]]" % (cmd, cmd, )
        control_str = ":foreach i in=[%s print as-value ] do=[:put [$i]]]" % (cmd,  )
        
        return self.ssh_cmd(control_str)

class ConfigEntityList:
    """List of entries on MikroTik."""

    def __init__(self, section, controller):
        """Set the controller instance and section of the list(eg. "/ip address"."""
        self.controller = controller
        self.section = section

    def load(self):
        """Load list of items from controller."""
        data = self.controller.load_entity_list(self.section)
        self.objects = self.parse(data)

    def new_item(self):
        """Create a new item and return it."""
        return ConfigEntity(self)

    def parse(self, data):
        """Parse the text form of list of items."""
        objs = data.split('\r\n')

        res = []
        for o in objs:
            # let the new entity to parse it's line
            n = self.new_item()
            n.parse(o)
            
            res.append(n)

        return res

    def cmd(self, cmd):
        """Execute @cmd."""
        return self.controller.ssh_cmd("%s %s" % (self.section, cmd, ) )


class ConfigEntity:
    """Holds information of one item of entity list (e.g. one interface, or one firewall rule, ...)."""
    _id = None
    _ce_list = None


    ignore_list = [ 'actual-interface', ]

    def __init__(self, ce_list):
        """Set the parent list instance attr."""
        self._ce_list = ce_list
        self.data = {}

    def set(self, attr, val):
        """Set attribute @attr of this item to @val."""
        self.data[attr] = val

    def get(self, attr):
        """Get attribute @att of this item."""
        if self.data.has_key(attr):
            return self.data[attr]
        else:
            raise Exception('attr does not exist: %s' % (attr))
    
    def parse(self, input):
        """Parse line with information."""
        self.data = {}
        vals = input.split(';')
        if len( input.strip() ) == 0:
            return

        for i in vals:
            k, v = i.split( '=', 1 )
            self.data[ k ] = v
        self._id = self.data[ '.id' ]
        return

        # bellow is code that did it for the command that is compatible with routeros 2.9 (see above)
        """        
        #remove comments and join the lines to make one
        lns = [ l for l in input.split('\r\n') if not (';;;' in l)  ]
        self._id = lns[0]
        data = " ".join(lns[1:])
        
        #extract attributes
        att_val = re.compile('(?P<attribute>[^ ]+)=(?P<value>[^ ]*)')
        vals = att_val.findall(data)
        for key, val in vals:
            self.data[key] = val
        """

    def save_as(self, id = None, before = None):
        """Save this item as an item with id @id."""
        return self._save(id, id == None, before = before)
    
    def save_as_new(self, before = None):
        """Save this item as a new item == save a copy."""
        return self.save_as( id = None, before = before)
    
    def save(self):
        """Save == commit changes."""
        return self._save(self._id)
    

    def _save(self, id, add = False, before = None):
        """Commit changes of this entity to the server."""
        val_lst = " ".join([ '%s="%s"' % (val, key) for val, key in self.data.items() if not (val in self.ignore_list) ])
        if add:            
            cmd = "add %s" % (val_lst )
            if before is not None:
                cmd += " place-before=%s" % (before,)
        else:
            cmd = "set %s %s" % (id, val_lst )
        print 'SAVING ', id, cmd
        print self._ce_list.cmd(cmd)
        print 'OK.'

    def delete(self):
        """Delete this entity from the server."""
        cmd = "remove %s" % (self._id)
        print 'REMOVE', self._id, cmd
        print self._ce_list.cmd(cmd)
        print 'OK.'

