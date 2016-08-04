# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .resource import BossResource, Collection, CoordinateFrame, Experiment, Channel, Layer
import json


class BossResourceBasic(BossResource):
    """
    Resource class primarily used when testing.  It takes a dictionary as an input to the constructor,
    and from this is able to populate all values as needed.

     Args:
      data (dict): a dictionary containing all the values to configure the resource

    Attributes:
      data (dict): a dictionary containing all the values to configure the resource
    """
    def __init__(self, data=None):
        # call the base class constructor
        BossResource.__init__(self)

        self.data = data

    def from_json(self, json_str):
        """
        Static method to populate a basic resource from a json string
        Args:
            json_str (str): JSON encoded resource

        Returns:
           (BossResourceBasic): An instantiated basic resource

        """
        self.data = json.loads(json_str)
        self._boss_key = self.data['boss_key']
        self._lookup_key = self.data['lookup_key']

    # Methods to populate class properties
    def populate_collection(self):
        """
        Method to create a Collection instance and set self._collection.
        """
        self._collection = Collection(self.data['collection']['name'],
                                      self.data['collection']['description'])

    def populate_coord_frame(self):
        """
        Method to create a CoordinateFrame instance and set self._coord_frame.
        """
        self._coord_frame = CoordinateFrame(self.data['coord_frame']['name'],
                                            self.data['coord_frame']['description'],
                                            self.data['coord_frame']['x_start'],
                                            self.data['coord_frame']['x_stop'],
                                            self.data['coord_frame']['y_start'],
                                            self.data['coord_frame']['y_stop'],
                                            self.data['coord_frame']['z_start'],
                                            self.data['coord_frame']['z_stop'],
                                            self.data['coord_frame']['x_voxel_size'],
                                            self.data['coord_frame']['y_voxel_size'],
                                            self.data['coord_frame']['z_voxel_size'],
                                            self.data['coord_frame']['voxel_unit'],
                                            self.data['coord_frame']['time_step'],
                                            self.data['coord_frame']['time_step_unit'])

    def populate_experiment(self):
        """
        Method to create a Experiment instance and set self._experiment.
        """
        self._experiment = Experiment(self.data['experiment']['name'],
                                      self.data['experiment']['description'],
                                      self.data['experiment']['num_hierarchy_levels'],
                                      self.data['experiment']['hierarchy_method'],
                                      self.data['experiment']['max_time_sample'],
                                      )

    def populate_channel_or_layer(self):
        """
        Method to create a Channel or Layer instance and set self._channel or self._layer.
        """
        if self.data['channel_layer']['is_channel']:
            # You have a channel request
            self._channel = Channel(self.data['channel_layer']['name'],
                                    self.data['channel_layer']['description'],
                                    self.data['channel_layer']['datatype'])
        else:
            # You have a layer request
            self._layer = Layer(self.data['channel_layer']['name'],
                                self.data['channel_layer']['description'],
                                self.data['channel_layer']['datatype'],
                                self.data['channel_layer']['base_resolution'],
                                self.data['channel_layer']['parent_channels'])

    def populate_boss_key(self):
        """
        Method to set self._boss_key.
        """
        self._boss_key = self.data['boss_key']

    def populate_lookup_key(self):
        """
        Method to set self._lookup_key.  Should be overridden.
        """
        self._lookup_key = self.data['lookup_key']

    # Methods to delete the entry from the data model tables
    def delete_collection_model(self):
        pass

    def delete_experiment_model(self):
        pass

    def delete_coord_frame_model(self):
        pass

    def delete_channel_layer_model(self):
        pass

