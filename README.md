## What makes ImageNet good for Transfer Learning?
This code provides a script to download our trained models for our paper 'What makes ImageNet good for Transfer Learning?'
You can find our paper at https://arxiv.org/abs/1608.08614 or visit our [project page](http://www.minyounghuh.com/papers/analysis/)

### Requirements
+ Python 2.7
+ nltk (optional)

### Downloading trained models
To download all our models run the code. 
```
python get_models.py
```
The code will sequentially download all the models and save it the directory ```./models```

To specify which models to download you can run the code with the flag ```-e```

```
# Downloads all the models for the hierarchy experiment
python get_models.py -e hierarchy

# Downloads all the models from the class experiment
python get_models.py -e class
```

To go one step further and select a specific experiment you can pass the flag ```-s```

```
# Downloads the model from the hierarchy experiment trained with 918 classes
python get_models.py -e hierarchy -s 918
```

You can also specify the save destination using the flag ```-d```
```
# Save the specific model on the destination ./dst
python get_models.py -e hierarchy -s 918 -d ./dst
```

### Label set generator and WordNet tools
We provide the code to generate the label sets mentioned in the hierarchy experiments.  

To generate the label sets yourself, you will need to download the python compatible WordNet corpus from https://wordnet.princeton.edu/wordnet/download/  
For some python examples on how to use WordNet, refer to http://www.nltk.org/howto/wordnet.html

We also include helper functions to easily manipulate wordnet tree in ```wordnet_tools.py```

To run the script to generate label sets
```
python make_labels.py
```

You can also specify the experiment
``` 
# By default -e is set to all
python make_labels.py -e up_down
python make_labels.py -e down_up
python make_labels.py -e all 
```

### PASCAL experiments
Common classes shared between PASCAL and ImageNet can be found [here](./label_sets/pascal)

### LMDB generation toolkit (coming soon)
Training a network by passing in images sequentially often becomes a bottleneck in training.
We provide a simple toolkit to generate LMDB
```
coming soon
```
