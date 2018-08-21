#! bin/bash
psql -d gem_cms_core_dev -c 'delete from activities;'
psql -d gem_cms_core_dev -c 'delete from agencies;'
psql -d gem_cms_core_dev -c 'delete from clients;'

psql -d gem_cms_core_dev -c '\copy clients from data/content/clients.csv csv header;'

psql -d gem_cms_core_dev -c '\copy agencies from data/content/agencies.csv csv header;'

psql -d gem_cms_core_dev -c '\copy activities from data/content/activities.csv csv header;'
