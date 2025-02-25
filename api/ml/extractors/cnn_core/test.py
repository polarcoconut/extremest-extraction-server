#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN
from computeScores import computeScores

# Parameters
# ==================================================

def test_cnn(test_examples, test_labels, checkpoint_file, vocabulary):
    # Eval Parameters
    #tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
    #tf.flags.DEFINE_string("checkpoint_dir", checkpoint_dir, "checkpoint directory from training run")

    # Misc Parameters
    #tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
    #tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")


    FLAGS = tf.flags.FLAGS
    FLAGS._parse_flags()
    print("\nParameters:")
    for attr, value in sorted(FLAGS.__flags.items()):
        print("{}={}".format(attr.upper(), value))
    print("")

    # Load data. Load your own data here
    print("Loading data...")
    x_test, y_test, vocabulary, vocabulary_inv = data_helpers.load_test_data(test_examples, test_labels, vocabulary)
    #x_test, y_test, vocabulary, vocabulary_inv = data_helpers.load_data()

    y_test = np.argmax(y_test, axis=1)
    print("Vocabulary size: {:d}".format(len(vocabulary)))
    print("Test set size {:d}".format(len(y_test)))

    print("\nEvaluating...\n")

    # Evaluation
    # ==================================================

    #checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)
    graph = tf.Graph()
    #with graph.as_default(), tf.device('/gpu:2'):
    with graph.as_default():
        #gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.10,
        #                            allow_growth = True)
        gpu_options = tf.GPUOptions(allow_growth = True)

        session_conf = tf.ConfigProto(
          allow_soft_placement=FLAGS.allow_soft_placement,
            log_device_placement=FLAGS.log_device_placement,
            gpu_options = gpu_options)
        sess = tf.Session(config=session_conf)
        with sess.as_default():
            # Load the saved meta graph and restore variables
            saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
            saver.restore(sess, checkpoint_file)

            # Get the placeholders from the graph by name
            input_x = graph.get_operation_by_name("input_x").outputs[0]
            # input_y = graph.get_operation_by_name("input_y").outputs[0]
            dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

            # Tensors we want to evaluate
            predictions = graph.get_operation_by_name("output/predictions").outputs[0]
            #normalized_scores = graph.get_operation_by_name("output/normalized_scores").outputs[0]            

            # Generate batches for one epoch
            batches = data_helpers.batch_iter(x_test, FLAGS.batch_size, 1, shuffle=False)

            # Collect the predictions here
            all_predictions = []
            all_normalized_scores = []

            for x_test_batch in batches:
                batch_predictions = sess.run(predictions, {input_x: x_test_batch, dropout_keep_prob: 1.0})
                all_predictions = np.concatenate([all_predictions, batch_predictions])
                #batch_normalized_scores = sess.run(normalized_scores, {input_x: x_test_batch, dropout_keep_prob: 1.0})
                #for batch_normalized_score in batch_normalized_scores:
                #    all_normalized_scores.append(batch_normalized_score)
                #all_normalized_scores += batch_normalized_scores


    # Print accuracy and fscores
    correct_predictions = float(sum(all_predictions == y_test))
    print("Total number of test examples: {}".format(len(y_test)))
    print("Accuracy: {:g}".format(correct_predictions/float(len(y_test))))

    """
    gold_labels = []
    for gold_label in y_test:
        gold_labels.append(np.argmax(gold_label))
    predicted_labels = []
    for prediction in all_predictions:
        predicted_labels.append(np.argmax(prediction))
    """

    return all_predictions, all_normalized_scores
    #precision, recall, fscore = computeScores(
    #    all_predictions, y_test)
    #print ("precision: %f, recall: %f, fscore: %f" % (
    #    precision, recall, fscore))

    #return precision, recall, fscore
