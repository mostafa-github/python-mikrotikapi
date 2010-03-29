#!/usr/bin/python
import datetime
from mtick_api.mtickapi import *
from mtick_api.libs import ListSync

class NeplaticiSync(ListSync):
    section = '/ip firewall address-list'
    
    def init(self):
        # populate @self.objlist with our data (addresses from DB in this case)
        self.objlist = [ '10.10.10.10', '10.10.10.11', '10.10.10.12', '10.10.0.0/24' ]
    
    def create_item(self, nitem, obj):
        # populate the new item @nitem with our data from @obj
        nitem.set( 'list', 'neplatic' )
        nitem.set( 'address', obj )
    
    def process_object(self, obj):
        """This method is used to go through all of the items that already exist on mtick
        in given section and were added by us."""

        # if the object is not our list neplatic, do nothing
        if obj.get('list') != 'neplatic':
            return 
        # check if this item is already on the list of our objects to sync,
        # if so, remove it from there (as not to add duplicates)
        try:
          self.objlist.remove( obj.get('address') )
        except ValueError:
          # not on list -> delete -- the object doesn't exist in our objects to sync
          obj.delete()
        except Exception:
          # does not have an attribute address -> continue
          return




if __name__ == "__main__":
    print 'updating mtick'
    p = NeplaticiSync('adresa', 22, 'admin', '<heslo>')
    p.sync()
