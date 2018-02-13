#
# The main Lambda to run on DeepLens.
#
import os, time, awscam, cv2, questions, voice
from threading import Timer
from threading import Thread

objects_to_consider_if_they_appear = questions.get_all_answers()
out_map = { 1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat', 5: 'bottle', 6: 'bus', 7 : 'car', 8 : 'cat', 9 : 'chair', 10 : 'cow', 11 : 'dinning table', 12 : 'dog', 13 : 'horse', 14 : 'motorbike', 15 : 'person', 16 : 'pottedplant', 17 : 'sheep', 18 : 'sofa', 19 : 'train', 20 : 'tvmonitor' }

# The algorithm is better at some objects than others,
# so a variable threshold for probability works best:
thresholds = {
    'aeroplane': 0.2,
    'bicycle': 0.25,
    'bird': 0.35,
    'boat': 0.15,
    'bottle': 0.5,
    'bus': 0.2,
    'car': 0.4,
    'cat': 0.45,
    'chair': 0.35,
    'cow': 0.35,
    'dinning table': 0.5,
    'dog': 0.5,
    'horse': 0.35,
    'motorbike': 0.35,
    'person': 0.5,
    'pottedplant': 0.35,
    'sheep': 0.3,
    'sofa': 0.7,
    'train': 0.15,
    'tvmonitor': 0.7
}

ret, frame = awscam.getLastFrame()
ret,jpeg = cv2.imencode('.jpg', frame)
Write_To_FIFO = True
class FIFO_Thread(Thread):
    def __init__(self):
        ''' Constructor. '''
        Thread.__init__(self)

    def run(self):
        print '** run() started'
        fifo_path = "/tmp/results.mjpeg"
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)
        f = open(fifo_path,'w')
        print '** Opened output file pipe'
        while Write_To_FIFO:
            try:
                f.write(jpeg.tobytes())
            except IOError as e:
                continue

def greengrass_infinite_infer_run():
    try:
        modelPath = "/opt/awscam/artifacts/mxnet_deploy_ssd_resnet50_300_FP16_FUSED.xml"
        modelType = "ssd"
        input_width = 300
        input_height = 300
        results_thread = FIFO_Thread()
        results_thread.start()
        print '** Object detection starts now'
        try:
            voice.say_phrase('loading')
            # threading.Thread(target=voice.say_phrase, args=('loading', )).start()
        except Exception as e:
            print '** Unable to say loading'

        mcfg = {"GPU": 1}
        model = awscam.Model(modelPath, mcfg)
        print '** Model loaded'
        ret, frame = awscam.getLastFrame()
        if ret == False:
            raise Exception("Failed to get frame from the stream")
        print '** Got last frame'
        yscale = float(frame.shape[0]/input_height)
        xscale = float(frame.shape[1]/input_width)

        firstGo = True
        spotted_objects_last_time = {}

        print '** Inference now starting'
        doInfer = True
        while doInfer:
            spotted_objects_this_time = {}
            if firstGo:
                print '** First time - about to play welcome message'
                try:
                    questions.intro()
                    # threading.Thread(target=questions.intro).start()
                except Exception as e:
                    print "!! Unable to play intro: " + str(e)
                print '** First time - finished playing welcome message'
                firstGo = False

            # Get a frame from the video stream
            ret, frame = awscam.getLastFrame()
            # Raise an exception if failing to get a frame
            if ret == False:
                print "!! Failed to get frame from the stream"
                raise Exception("Failed to get frame from the stream")

            # Resize frame to fit model input requirement
            frameResize = cv2.resize(frame, (input_width, input_height))

            # Run model inference on the resized frame
            inferOutput = model.doInference(frameResize)

            # Output inference result to the fifo file so it can be viewed with mplayer
            parsed_results = model.parseResult(modelType, inferOutput)['ssd']

            # print "Before parsed results..."
            for obj in parsed_results:
                object_name = out_map[obj['label']]
                if object_name in thresholds:
                    if obj['prob'] > thresholds[object_name]:
                        object_name = out_map[obj['label']]
                        spotted_objects_this_time[object_name] = obj['prob']
                        xmin = int( xscale * obj['xmin'] ) + int((obj['xmin'] - input_width/2) + input_width/2)
                        ymin = int( yscale * obj['ymin'] )
                        xmax = int( xscale * obj['xmax'] ) + int((obj['xmax'] - input_width/2) + input_width/2)
                        ymax = int( yscale * obj['ymax'] )
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (255, 165, 20), 4)
                        label_show = "XX:{}:    {:.2f}%".format(object_name, obj['prob']*100 )
                        cv2.putText(frame, label_show, (xmin, ymin-15),cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 165, 20), 4)

            global jpeg
            ret,jpeg = cv2.imencode('.jpg', frame)
            # print "...parsing results finished"
            try:
                considerChangeInObjects(spotted_objects_last_time, spotted_objects_this_time)
            except Exception as e:
                print '!! Problem considering change in objects: ' + str(e)
            spotted_objects_last_time = spotted_objects_this_time

    except IOError as e:
        print "FATAL I/O error({0}): {1}".format(e.errno, e.strerror)
    except ValueError as e:
        print "FATAL ValueError: " + str(e)
    except 0:
        print "Got a 0"
        traceback.print_exc()
    except Exception as e:
        print "The non-0 exception was", e
        print "Oh well - now running again:"
        greengrass_infinite_infer_run()

    # Asynchronously schedule this function to be run again in 15 seconds
    Timer(15, greengrass_infinite_infer_run).start()

def considerChangeInObjects(spotted_objects_last_time, spotted_objects_this_time):
    # print "LAST TIME:"
    # print spotted_objects_last_time
    # print "THIS TIME:"
    # print spotted_objects_this_time
    new_objects = {}
    for name, probability in spotted_objects_this_time.iteritems():
        if not name in spotted_objects_last_time:
            new_objects[name] = probability

    if len(new_objects) > 0:
        # print "NEW THINGS:"
        # print new_objects
        try:
            handle_new_objects(new_objects)
        except Exception as e:
            print '!! Problem handling new objects: ' + str(e)
    else:
        try:
            questions.consider_repeating_question()
            # threading.Thread(target=questions.consider_repeating_question).start()
        except Exception as e:
            print "!! Cannot repeat question: " + str(e)


def handle_new_objects(new_objects):
    best_object_name = None
    best_object_probability = None
    for name, probability in new_objects.iteritems():
        if name in objects_to_consider_if_they_appear:
            print "I HAVE FOUND A " + name + " with probability " + str(probability)
            print "best_object_name:" + str(best_object_name)
            print "best_object_probability:" + str(best_object_probability)
            if best_object_name == None or probability > best_object_probability:
                print "Time to set..."
                best_object_name = name
                best_object_probability = probability

    if best_object_name != None:
        try:
            print "Considering the answer " + best_object_name
            # threading.Thread(target=questions.mark_answer, args=(best_object_name, )).start()
            questions.mark_answer(best_object_name)
        except Exception as e:
            print "!! Could not mark answer " + best_object_name + ": " + str(e)

# Execute the function above
greengrass_infinite_infer_run()

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    return
