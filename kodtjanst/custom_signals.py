from pdb import set_trace
from django.dispatch import receiver
from django.db.models.signals import post_save
import os 

def has_uploaded_file_been_deleted(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
        if obj.underlag.name == '': # model has no associated file
           pass
        else:
            try:
                if obj.underlag.name != instance.underlag.name: # file is cleared on model / changed to new file
                    if obj.underlag.name is not None:
                        print(f"File paths are different, deleting file {obj.underlag.name}, and replacing with {instance.underlag.name}")
                        os.remove(obj.underlag.path)
            except ValueError as e:
                logger.error(e, f'Problem deleting file {obj.underlag.path}')
                return "Could not delete file"
    except sender.DoesNotExist:
        pass