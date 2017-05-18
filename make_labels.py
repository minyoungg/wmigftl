from nltk.corpus import wordnet
import wordnet_tools as wnt
import numpy as np
import os, copy, argparse

def make_up_down_labels(save_dir='./label_sets/hierarchy', depth=3):
    """
	Generates label set by traversing all wnid to its parent node and clustering
    all nodes that is a child. Since the minimum depth of imagenet is 3, there
    can only be 3 label sets. Because some parents have only 1 child, even after
    clustering, the new label may have the same number of examples. You can think
    of this method as clustering from top level, by fixing a height.
	"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    synset_path = os.path.join('./label_sets', 'synset_words.txt')
    train_path  = os.path.join('./label_sets', 'train.txt')
    val_path    = os.path.join('./label_sets', 'val.txt')

    synset_list = wnt.read_synset_file(synset_path)
    original_synset_list = list(synset_list)
    print 'Input :', len(set(original_synset_list)), 'labels'

    for d in range(depth):
        # Traverse up all wnid by 1 parent
        parent_wnids = [wnt.get_parent_wnid(wnid) for wnid in synset_list]

        # Cluster
        for j in range(len(parent_wnids)):
            current_wnid = parent_wnids[j]
            current_synset = wnt.wnid_to_synset(current_wnid)
            for k in range(len(parent_wnids)):
                check_synset = wnt.wnid_to_synset(parent_wnids[k])
                if wnt.is_hyponym(check_synset, current_synset):
                    parent_wnids[k] = parent_wnids[j]
        synset_list  = parent_wnids
        unique_wnids = list(set(parent_wnids))
        num_classes  = len(set(unique_wnids))

        print 'Clustered :', num_classes, 'labels'

        old_new_wnid_dict = {}       # old wnid --> new wnid
        old_label_new_wnid_dict = {} # old label --> new wnid
        new_wnid_label_dict = {}     # new wnid --> new label

        # maps old wnid -> new wnid
        for old_wnid, new_wnid in zip(original_synset_list, synset_list):
            old_new_wnid_dict[old_wnid] = new_wnid

        # maps new wnid to new label (for making synset word file)
        new_synsets_word_file, new_synsets_file = [], []
        for i in range(num_classes):
            wnid = unique_wnids[i]
            new_wnid_label_dict[wnid] = i
            new_synsets_file.append(wnid)
            synset_noun = wnid + ' ' + wnt.wnid_to_noun(wnid)
            new_synsets_word_file.append(synset_noun)

        # make train set
        new_train_file = []
        for line in open(train_path, 'r'):
            path, label = line.split()
            new_train_wnid = old_new_wnid_dict[path.split('/')[0]]
            new_label = new_wnid_label_dict[new_train_wnid]
            new_train_file.append(path + ' ' + str(new_label))

            # map old label -> new label
            if label not in old_label_new_wnid_dict.keys():
                old_label_new_wnid_dict[label] = new_train_wnid

        # make val set
        new_val_file = []
        for line in open(val_path, 'r'):
            path, label = line.split()
            new_wnid = old_label_new_wnid_dict[label]
            new_label = new_wnid_label_dict[new_wnid]
            new_val_file.append(path + ' ' + str(new_label))

        np.savetxt(os.path.join(save_dir, 'train_up_down_'+str(num_classes)+'.txt'),
                   new_train_file, delimiter=" ", fmt="%s")
        np.savetxt(os.path.join(save_dir, 'val_up_down_'+str(num_classes)+'.txt'),
                   new_val_file, delimiter=" ", fmt="%s")
        np.savetxt(os.path.join(save_dir, 'synset_words_up_down_'+str(num_classes)+'.txt'),
                   new_synsets_word_file, delimiter=" ", fmt="%s")
    print 'Done.'
    return

def make_down_up_labels(save_dir='./label_sets/hierarchy'):
    """
    Generates label sets for the hierarchy experiment. From deepest depth to the
    root node, the function traverses the wordnet tree and clusters all nodes
    below current depth to the ancestor node at the current depth.
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    all_wnids = wnt.read_synset_file(os.path.join('./label_sets', 'synset_words.txt'))
    stats = wnt.wnid_statistics(all_wnids)
    num_examples = len(all_wnids)

    current_max_depth = stats['max_depth']
    depth_array = stats['depth_arr'] # depth of each wnid in the label set

    # used to maps previous wnid to the next wnid
    current_wnid_array = copy.deepcopy(all_wnids)

    # used to maps previous level wnid to next level wnid
    wnid_mapper = {wnid:wnid for wnid in all_wnids}

    prev_train_file = wnt.read_txt_file(os.path.join('./label_sets', 'train.txt'))
    prev_val_file = wnt.read_txt_file(os.path.join('./label_sets', 'val.txt'))
    lbl_to_wnid_mapper = {}

    for line in prev_train_file:
        path,label = line.split(' ')
        lbl_to_wnid_mapper[label] = path.split('/')[0]

    # climb up from the lowest depth
    for level in range(current_max_depth):
        print 'Current depth traversal', level + 1

        # generate a mapping between previous wnid to the next wnid
        for i in range(num_examples):
            if depth_array[i] == current_max_depth:
                current_wnid = current_wnid_array[i]
                new_wnid = wnt.get_parent_wnid(current_wnid)
                current_wnid_array[i] = new_wnid
                depth_array[i] = current_max_depth-1
                wnid_mapper[current_wnid] = new_wnid

        current_max_depth -= 1
        unique_synset = set(current_wnid_array)
        num_classes = len(unique_synset)

        # generate synset word file
        synset_words_file = [wnid + ' ' + wnt.wnid_to_noun(wnid) for wnid in unique_synset]
        file_name = os.path.join(save_dir, 'synset_words_down_up_'+str(num_classes)+'.txt')
        np.savetxt(file_name, synset_words_file, delimiter=" ", fmt="%s")

        # mapper for new labels
        new_wnid_to_lbl_mapper = {wnid:str(i) for i,wnid in enumerate(unique_synset)}

        # mapper for old label to new label
        old_to_new_lbl_mapper = {}

        # make train set
        train_file = []
        for line in prev_train_file:
            path, old_label = line.split(' ')
            prev_wnid = lbl_to_wnid_mapper[old_label]
            new_wnid =  wnid_mapper[prev_wnid]
            new_label = new_wnid_to_lbl_mapper[new_wnid]
            train_file.append(path + ' ' + new_label)
            old_to_new_lbl_mapper[old_label] = new_label

        np.savetxt(os.path.join(save_dir, 'train_down_up_'+str(num_classes)+'.txt'),
                    train_file, delimiter=' ', fmt="%s")

        # make val set
        val_file = []
        for line in prev_val_file:
            path, old_label = line.split(' ')
            new_line = path + ' ' + old_to_new_lbl_mapper[old_label]
            val_file.append(new_line)

        np.savetxt(os.path.join(save_dir,'val_down_up_'+str(num_classes)+'.txt'),
                    val_file, delimiter=' ', fmt="%s")

        prev_val_file = val_file
        prev_train_file = train_file
        lbl_to_wnid_mapper = dict((v,k) for k,v in new_wnid_to_lbl_mapper.iteritems())
    print 'Done.'
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download trained models for WMIGFT")
    parser.add_argument("-e", "--experiment", default='all',
        help="Choose from (up_down, down_up, all). If flag is not specified\
              all will be chosen by default. For more information on how label\
              sets are created read the documentation in make_labels.py or the paper")

    args = parser.parse_args()
    if args.experiment in ('up_down', 'all'):
        print 'Generating label sets for up_down hierarchy experiments'
        continue
        make_up_down_labels()
    if args.experiment in ('down_up', 'all'):
        print 'Generating label sets for down_up hierarchy experiments'
        continue
        make_down_up_labels()
    else:
        print 'Invalid -e flag'
        paraser.print_help()
