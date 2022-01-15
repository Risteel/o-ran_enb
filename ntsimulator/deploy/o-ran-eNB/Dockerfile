#
# Copyright 2020 highstreet technologies GmbH and others
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

################
#### DEVICE ####
################

FROM o1_base:latest
LABEL maintainer="alexandru.stancu@highstreet-technologies.com / adrian.lita@highstreet-technologies.com"

# ntsim-ng configuration and deployment
COPY ./yang /opt/dev/deploy/yang
COPY ./data /opt/dev/deploy/data
COPY ./config.json /opt/dev/ntsim-ng/config/config.json
COPY ./watchfile.py /opt/dev/workspace/watchfile.py

# ntsim-ng init docker
RUN /opt/dev/ntsim-ng/ntsim-ng --container-init -w /opt/dev/ntsim-ng
RUN pip3 install --upgrade setuptools
RUN pip3 install paho-mqtt
RUN pip3 install requests
RUN pip3 install -U watchdog
RUN mkdir /opt/dev/workspace/o-ran-enb

COPY ./event-settings_send.json /opt/dev/workspace/o-ran-enb/event-settings_send.json
COPY ./event-settings_no_send.json /opt/dev/workspace/o-ran-enb/event-settings_no_send.json
COPY ./ue_net_switch_to_cellular.sh /opt/dev/workspace/ue_net_switch_to_cellular.sh
# finishing container build
ARG BUILD_DATE
LABEL build-date=$BUILD_DATE

# add exposed ports
EXPOSE 830-929
EXPOSE 21-22

ENV NTS_FUNCTION_TYPE=NTS_FUNCTION_TYPE_O_RAN_O_DU

# run
WORKDIR /opt/dev/workspace
CMD ["/opt/dev/ntsim-ng/ntsim-ng", "-w/opt/dev/ntsim-ng", "--supervisor"]