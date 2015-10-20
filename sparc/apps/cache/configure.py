from sparc.common import Configure as ConfigureSparc
import sparc.apps.cache

def Configure(zcml_list = None):
    """Setup Zope Component global registry
    
    Args:
        zcml_list: list of tuples whose first entry is the python package to
                   be configured, and whose optional 2nd entry is the 
                   zcml file name (defaults to configure.zcml) to perform the
                   configuration for.
    """
    zcml_list = zcml_list if zcml_list else []
    zcml_list = [
               (sparc.apps.cache)
               ] + zcml_list
    return ConfigureSparc(zcml_list)
    
