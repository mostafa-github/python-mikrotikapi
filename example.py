import datetime
from mtick_api.mtickapi import *
from mtick_api.libs import ListSync

class NeplaticiSync(ListSync):
    section = '/ip firewall address-list'
    
    def init(self):
        # populate @self.objlist with our data (addresses from DB in this case)
        self.objlist = Neplatici().get()
    
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


# sezene seznam neplaticu
import psycopg2
DBNAME = ""
HOST = ""
USER = ""
PASSWORD = ""

query = """
SELECT DISTINCT 
  klientska_zarizeni.ip
FROM
  klientska_zarizeni
  INNER JOIN platby ON (klientska_zarizeni.clen = platby.clen)
  INNER JOIN aktualni_splatnost ON (klientska_zarizeni.clen = aktualni_splatnost.varsym)
WHERE
  platby.vyjimka = 'f' AND 
  platby.ma_dati - platby.dal > 0 AND 
  aktualni_splatnost.splatnost < now();
"""

class Neplatici(object):
  def get( self ):
      # connect
      try:
        con = psycopg2.connect("dbname='%s' host='%s' user='%s' password='%s'" % ( DBNAME, HOST, USER, PASSWORD, ) )
        c = con.cursor()
        c.execute( query )
        print query
        res = c.fetchall()
      except Exception, e:
        print 'err', e
        return

      return [ i[ 0 ] for i in res ]





if __name__ == "__main__":
    print 'updating mtick'
    p = NeplaticiSync('adresa', 22, 'admin', '<heslo>')
    p.sync()
