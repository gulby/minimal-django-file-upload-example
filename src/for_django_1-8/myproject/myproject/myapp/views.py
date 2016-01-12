# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from myproject.myapp.models import Document
from myproject.myapp.forms import DocumentForm

import sys
caffe_home = '/home/lleo52/caffe'
documents_home = '/home/lleo52/minimal-django-file-upload-example/src/for_django_1-8/myproject/media'
sys.path.append('%s/python' % caffe_home)
import caffe
import numpy as np

def list(request):
    # gulby
    results = None
    model_def = '%s/gulby/uspace3_vgg16_original.prototxt' % caffe_home
    pretrained_model = '%s/gulby/uspace_50_final_add.caffemodel' % caffe_home
    label_file = '%s/gulby/labels_only_name.txt' % caffe_home
    images_dim = '256,256'
    input_scale = None
    raw_scale = 255.0
    channel_swap = '2,1,0'
    
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # gulby
            test_file = newdoc.docfile.name
            image_dims = [int(s) for s in images_dim.split(',')]
            mean = np.ndarray(shape=(3), dtype=float)
            mean[0] = 104
            mean[1] = 117
            mean[2] = 123
            channel_swap = [int(s) for s in channel_swap.split(',')]
            caffe.set_mode_cpu()
            classifier = caffe.Classifier(model_def, pretrained_model, image_dims=image_dims, mean=mean, input_scale=input_scale, raw_scale=raw_scale, channel_swap=channel_swap)
            np_result = classifier.predict([caffe.io.load_image('%s/%s' % (documents_home, test_file))], True).flatten()
            #print(np_result)
            labels = np.loadtxt(label_file, str, delimiter='\t')
            #print(np_result.argsort()[-1:-6:-1])

            #results = labels[np_result.argsort()[-1:-4:-1]]
            results = ['%s : %2.2f%%' % (labels[i], np_result[i]*100) for i in np_result.argsort()[-1:-4:-1]]
            
            # Redirect to the document list after POST
            #return HttpResponseRedirect(reverse('myproject.myapp.views.list'))
            
            return render_to_response(
                'list.html',
                {'form': form, 'results': results},
                context_instance=RequestContext(request)
            )
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
