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

import unittest
from unittest.mock import patch
from mockredis import mock_strict_redis_client

from spdb.project import BossResourceBasic
from spdb.spatialdb import CacheStateDB

import redis

from bossutils import configuration
from spdb.project.test.resource_setup import get_image_dict


class CacheStateDBTestMixin(object):

    def test_add_cache_misses(self):
        """Test if cache cuboid keys are formatted properly"""
        csdb = CacheStateDB(self.config_data)
        assert not self.state_client.get("CACHE-MISS")

        keys = ['key1', 'key2', 'key3']

        csdb.add_cache_misses(keys)

        for k in keys:
            assert k == self.state_client.lpop("CACHE-MISS").decode()

    def test_project_locked(self):
        """Test if a channel/layer is locked"""
        csdb = CacheStateDB(self.config_data)

        assert csdb.project_locked("1&1&1") == False

        csdb.set_project_lock("1&1&1", True)

        assert csdb.project_locked("1&1&1") == True

        csdb.set_project_lock("1&1&1", False)

        assert csdb.project_locked("1&1&1") == False

    def test_add_to_page_out(self):
        """Test if a cube is in page out"""
        csdb = CacheStateDB(self.config_data)

        temp_page_out_key = "temp"
        lookup_key = "1&1&1"
        resolution = 1
        morton = 234
        time_sample = 1

        page_out_key = "PAGE-OUT&{}&{}".format(lookup_key, resolution)
        assert not self.state_client.get(page_out_key)

        assert not csdb.in_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)

        in_page_out = csdb.add_to_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)
        assert not in_page_out

        assert csdb.in_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)

    def test_remove_from_page_out(self):
        """Test removing a cube from the page out list"""
        csdb = CacheStateDB(self.config_data)

        temp_page_out_key = "temp"
        lookup_key = "1&2&3"
        resolution = 4
        morton = 1000
        time_sample = 5

        page_out_key = "PAGE-OUT&{}&{}".format(lookup_key, resolution)
        assert not self.state_client.get(page_out_key)

        assert not csdb.in_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)

        in_page_out = csdb.add_to_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)
        assert not in_page_out

        assert csdb.in_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)

        # Fake the write-cuboid key
        csdb.remove_from_page_out("WRITE-CUBOID&{}&{}&{}&{}&adsf34adsf49sdfj".format(lookup_key, resolution, time_sample, morton))
        assert not csdb.in_page_out(temp_page_out_key, lookup_key, resolution, morton, time_sample)

    def test_add_to_delayed_write(self):
        """Test if a cube is in delayed write"""
        csdb = CacheStateDB(self.config_data)

        lookup_key = "1&2&3"
        resolution = 4
        time_sample = 5
        morton = 66
        write_cuboid_key1 = "WRITE-CUBOID&{}&{}&{}&{}&daadsfjk".format(lookup_key,
                                                                    resolution,
                                                                    time_sample,
                                                                    morton)
        write_cuboid_key2 = "WRITE-CUBOID&{}&{}&{}&{}&fghfghjg".format(lookup_key,
                                                                    resolution,
                                                                    time_sample,
                                                                    morton)

        keys = csdb.get_all_delayed_write_keys()
        assert not keys

        csdb.add_to_delayed_write(write_cuboid_key1, lookup_key, resolution, morton, time_sample, "{dummy resource str}")
        csdb.add_to_delayed_write(write_cuboid_key2, lookup_key, resolution, morton, time_sample, "{dummy resource str}")

        keys = csdb.get_all_delayed_write_keys()
        assert len(keys) == 1
        assert keys[0] == "DELAYED-WRITE&{}&{}&{}&{}".format(lookup_key,
                                                             resolution,
                                                             time_sample,
                                                             morton)

        write_keys = csdb.get_delayed_writes(keys[0])
        assert len(write_keys) == 2
        assert write_keys[0] == write_cuboid_key1
        assert write_keys[1] == write_cuboid_key2

    def test_get_all_delayed_write_cuboid_keys(self):
        """Test getting all delayed write cuboid keys"""
        csdb = CacheStateDB(self.config_data)

        lookup_key = "1&2&3"
        resolution = 4
        time_sample = 5
        morton = 234
        write_cuboid_key1 = "WRITE-CUBOID&{}&{}&{}{}&&daadsfjk".format(lookup_key,
                                                                       resolution,
                                                                       time_sample,
                                                                       morton)
        write_cuboid_key2 = "WRITE-CUBOID&{}&{}&{}&{}&fghfghjg".format(lookup_key,
                                                                       resolution,
                                                                       time_sample,
                                                                       morton)
        write_cuboid_key3 = "WRITE-CUBOID&{}&{}&{}&{}&aaauihjg".format(lookup_key,
                                                                       resolution,
                                                                       time_sample,
                                                                       morton)

        delayed_write_key = "DELAYED-WRITE&{}&{}&{}&{}".format(lookup_key,
                                                              resolution,
                                                              time_sample,
                                                              morton)

        keys = csdb.get_delayed_writes(delayed_write_key)
        assert not keys

        csdb.add_to_delayed_write(write_cuboid_key1, lookup_key, resolution, morton, time_sample, "{dummy resource str}")
        csdb.add_to_delayed_write(write_cuboid_key2, lookup_key, resolution, morton, time_sample, "{dummy resource str}")
        csdb.add_to_delayed_write(write_cuboid_key3, lookup_key, resolution, morton, time_sample, "{dummy resource str}")

        keys = csdb.get_delayed_writes(delayed_write_key)
        assert len(keys) == 3
        assert keys[0] == write_cuboid_key1
        assert keys[1] == write_cuboid_key2
        assert keys[2] == write_cuboid_key3

        keys = csdb.get_delayed_writes(delayed_write_key)
        assert not keys

    def test_get_single_delayed_write_cuboid_key(self):
        """Test getting all delayed write cuboid keys"""
        csdb = CacheStateDB(self.config_data)

        lookup_key = "1&2&3"
        resolution = 4
        time_sample = 5
        morton = 234
        write_cuboid_key1 = "WRITE-CUBOID&{}&{}&{}{}&&daadsfjk".format(lookup_key,
                                                                       resolution,
                                                                       time_sample,
                                                                       morton)
        write_cuboid_key2 = "WRITE-CUBOID&{}&{}&{}&{}&fghfghjg".format(lookup_key,
                                                                       resolution,
                                                                       time_sample,
                                                                       morton)
        write_cuboid_key3 = "WRITE-CUBOID&{}&{}&{}&{}&aaauihjg".format(lookup_key,
                                                                       resolution,
                                                                       time_sample,
                                                                       morton)

        delayed_write_key = "DELAYED-WRITE&{}&{}&{}&{}".format(lookup_key,
                                                              resolution,
                                                              time_sample,
                                                              morton)

        key = csdb.check_single_delayed_write(delayed_write_key)
        assert not key

        csdb.add_to_delayed_write(write_cuboid_key1, lookup_key, resolution, morton, time_sample, "{dummy resource str}")
        csdb.add_to_delayed_write(write_cuboid_key2, lookup_key, resolution, morton, time_sample, "{dummy resource str}")
        csdb.add_to_delayed_write(write_cuboid_key3, lookup_key, resolution, morton, time_sample, "{dummy resource str}")
        csdb.add_to_delayed_write(write_cuboid_key3, lookup_key, resolution, morton, 67, "{dummy resource str4}")

        key = csdb.check_single_delayed_write(delayed_write_key)
        assert key == write_cuboid_key1

        key = csdb.check_single_delayed_write(delayed_write_key)
        assert key == write_cuboid_key1

        key, resource = csdb.get_single_delayed_write(delayed_write_key)
        assert key == write_cuboid_key1
        assert resource == "{dummy resource str}"

        key, resource = csdb.get_single_delayed_write(delayed_write_key)
        assert key == write_cuboid_key2
        assert resource == "{dummy resource str}"

        key, resource = csdb.get_single_delayed_write(delayed_write_key)
        assert key == write_cuboid_key3
        assert resource == "{dummy resource str}"


@patch('redis.StrictRedis', mock_strict_redis_client)
class TestCacheStateDB(CacheStateDBTestMixin, unittest.TestCase):

    @classmethod
    @patch('redis.StrictRedis', mock_strict_redis_client)
    def setUpClass(cls):
        """Setup the redis client at the start of the test"""
        cls.data = get_image_dict()
        cls.resource = BossResourceBasic(cls.data)

        cls.config = configuration.BossConfig()

        cls.state_client = redis.StrictRedis(host=cls.config["aws"]["cache-state"], port=6379, db=1,
                                             decode_responses=False)

        cls.config_data = {"state_client": cls.state_client}

    def setUp(self):
        """Clean out the cache DB between tests"""
        self.patcher = patch('redis.StrictRedis', mock_strict_redis_client)
        self.mock_tests = self.patcher.start()

        self.state_client.flushdb()

    def tearDown(self):
        self.mock_tests = self.patcher.stop()

