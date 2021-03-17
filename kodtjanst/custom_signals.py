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
                    print(f"File paths are different, removing file {obj.underlag.name}, and replacing with {instance.underlag.name}")
                    if os.path.exists(obj.underlag.path):
                        os.remove(obj.underlag.path)
            except ValueError as e:
                print(e, f'Problem deleting file {obj.underlag.path}')
    except sender.DoesNotExist:
        pass