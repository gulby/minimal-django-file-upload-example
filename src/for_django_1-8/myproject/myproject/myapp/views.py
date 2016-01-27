# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse

from myproject.myapp.models import Document
from myproject.myapp.forms import DocumentForm

import sys
caffe_home = '/home/azureroot/caffe'
#caffe_home = '/home/gulby/caffe'
documents_home = '/home/azureroot/minimal-django-file-upload-example/src/for_django_1-8/myproject/media'
#documents_home = '/home/gulby/git/Temp/django/minimal-django-file-upload-example/src/for_django_1-8/myproject/media'
sys.path.append('%s/python' % caffe_home)
import caffe
import numpy as np
import json
from django.views.decorators.csrf import csrf_exempt
import MySQLdb

@csrf_exempt
def list(request):
    # gulby
    results = None
    results2 = None
    model_def = '%s/gulby/uspace3_vgg16_original.prototxt' % caffe_home
    pretrained_model = '%s/gulby/uspace_50_final_add_aug_ft2_8800.caffemodel' % caffe_home
    label_file = '%s/gulby/labels_only_name.txt' % caffe_home
    images_dim = '256,256'
    input_scale = None
    raw_scale = 255.0
    channel_swap = '2,1,0'
    
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            # address
            #print('address : %s' % request.POST['newaddr'])
            db = MySQLdb.connect(host="127.0.0.1", port=3306, user="root", passwd="", db="address")
            db.query("set character_set_connection=utf8;")
            db.query("set character_set_server=utf8;")
            db.query("set character_set_client=utf8;")
            db.query("set character_set_results=utf8;")
            db.query("set character_set_database=utf8;")
            cursor = db.cursor()
            new_addr = request.POST['newaddr'].replace(' ', '')
            query = u"select place_name from place where new_addr like '%s%%' limit 5" % new_addr
            #print u"query : %s " % query
            cursor.execute(query.encode('utf8'))
            raw_result = cursor.fetchall()
            results2 = ['%s : %2.2f%%' % (r[0], 0.5/len(raw_result)*100) for r in raw_result[:5]]
            results = {}
            for i, t in enumerate(raw_result[:5]):
                results['top%d' % (i+1)] = (t[0], '%f' % (0.5/len(raw_result)))
            db.close()

            # uspace
            #'''
            if (new_addr.startswith(u'경기도성남시분당구대왕판교로660') or new_addr.startswith(u'경기도성남시분당구대왕판교로670')) and 'docfile' in request.FILES:
                newdoc = Document(docfile=request.FILES['docfile'])
                newdoc.save()
                test_file = newdoc.docfile.name
                image_dims = [int(s) for s in images_dim.split(',')]
                mean = np.ndarray(shape=(3), dtype=float)
                mean[0] = 104
                mean[1] = 117
                mean[2] = 123
                channel_swap = [int(s) for s in channel_swap.split(',')]
                caffe.set_mode_cpu()
                #caffe.set_mode_gpu()
                classifier = caffe.Classifier(model_def, pretrained_model, image_dims=image_dims, mean=mean, input_scale=input_scale, raw_scale=raw_scale, channel_swap=channel_swap)
                np_result = classifier.predict([caffe.io.load_image('%s/%s' % (documents_home, test_file))], True).flatten()
                #print(np_result)
                labels = np.loadtxt(label_file, str, delimiter='\t')
                #print(np_result.argsort()[-1:-6:-1])
    
                results2 = labels[np_result.argsort()[-1:-6:-1]]
                results2 = ['%s : %2.2f%%' % (labels[i], np_result[i]*100/2) for i in np_result.argsort()[-1:-6:-1]]
                results = {}
                for i, t in enumerate(np_result.argsort()[-1:-6:-1]):
                    results['top%d' % (i+1)] = (labels[t], '%f' % (np_result[t]/2))
                
                # Redirect to the document list after POST
                #return HttpResponseRedirect(reverse('myproject.myapp.views.list'))
            #'''

            if request.POST['resulttype'] == 'html':
                return render_to_response(
                    'list.html',
                    {'form': form, 'results': results2},
                    context_instance=RequestContext(request)
                )
            else:
                return JsonResponse(results)
    else:
        form = DocumentForm()  # A empty, unbound form

    # Render list page with the documents and the form
    labels = np.loadtxt(label_file, str, delimiter='\t')
    results = labels
    return render_to_response(
        'list.html',
        {'form': form, 'results': results},
        context_instance=RequestContext(request)
    )
