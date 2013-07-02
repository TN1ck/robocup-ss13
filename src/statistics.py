import logging
import numpy

class Statistics:
    def __init__(self):
        self.abweichung = []
    #some basic statistics for the perception
    def print_results(self):
        #cut the start, because of long range beaming for positioning
        self.abweichung = self.abweichung[3:]

        logging.debug('Perception statisitcs:')
        logging.debug('based on ' + str(len(self.abweichung))+ ' points')
        average_error = 0
        for v in self.abweichung:
            average_error += numpy.linalg.norm(v) 
        average_error /= len(self.abweichung)
        logging.debug('Average position error: ' + str(average_error))

        max_error = 0
        for v in self.abweichung:
            e = numpy.linalg.norm(v) 
            if e > max_error:
                max_error = e
        logging.debug('maximaler Fehler: ' + str(max_error))

        #average error in the last 6 sek (our world memory)
        length = 100
        average_error = 0
        i = 0
        for v in self.abweichung:
            if i < length:
                average_error += numpy.linalg.norm(v) 
            else:
                average_error /= length
                logging.debug('Average position error ervery '+ str(length*0.06) + 's (' +str(length) + ' cycles): ' + str(round(average_error,4)))
                i = 0
            i += 1