from mtickapi import *


class ListSync(object):
    """List synchronization abstract class (list=interface list, nat rules, ...).
    that after implementing a few of its methods takes care of synchronization of your list
    to the MikroTik device."""
    section = '' # section on mtick. e.g. "/ip address"
    idcomment = 'steadydynamic' # comment string that will denote our entries
    objlist = None # list of your objects to be synchronized (each item on this list should be
                   # exactly one item on mikrotik)
    dst_host = None
    
    def init(self):
        """Called after the class is created. If you need to initialize the source of your data
        do it by overriding this method, rather than overriding the __init__. Fill the
        @self.objlist here with a list of your objects or an iterable."""
        raise NotImplementedError

    def create_item(self, nitem, obj):
        """Called whenever a newly created object needs to be filled with your data.
        @nitem is the new object, obj is your object from @self.objlist"""
        raise NotImplementedError

    def process_object(self, obj):
        """Called when going through already existing items in the list in the given @self.section on
        the device. You need to remove the object from @self.objlist if the object already exists in order
        not to add it twice, or if the object doesn't exist in your list you should delete it."""
        raise NotImplementedError

    def __init__(self, dst_host, dst_port, username, password ):
        """Setup the connection properties and initialize the objects."""
        self.dst_host = dst_host
        self.dst_port = dst_port
        self.username = username
        self.password = password
        self.objlist = []
        self.init()

    def sync(self):
        """Synchronize the lists."""
        # setup the connection to the mikrotik
        m = MikrotikController(ip = self.dst_host, port = self.dst_port, username = self.username, password = self.password)

        # load the list entries from the mikrotik from the given section
        cel = ConfigEntityList(self.section, m)
        cel.load()

        # for each existing list entry
        for obj in cel.objects:
            # check if it is our entry
            try:
                if obj.get('comment') != self.idcomment:
                    continue
                # if so, do some processing (e.g. deleting from objects to be added, deleting it, ... )
                self.process_object(obj)
            except:
                #apparently it doesn't have comment -> not our boy
                continue
            

        # for each item on @self.objlist
        for o in self.objlist:
            # create a new item
            nitem = cel.new_item()
            # fill it with data
            self.create_item(nitem, o)
            # mark it so that we can recognize it anytime later
            nitem.set( 'comment', self.idcomment )
            # save it to mtick
            nitem.save_as_new()
