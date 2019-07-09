.. _faq:

==========================
Frequently Asked Questions
==========================
**Q: How can I mount a shared Windows folder?**

We recommend that you install cifs-utils, by using the following command:

.. code:: console
	
	$ apt-get install cifs-utils 

Afterwards you can mount the folder using the following command:

.. code:: console

	$ mount -t cifs -o username=username //server-name/sharename /mountpoint

**Q: How can I access my lxc localhost from a browser on the host machine?**

Instead of starting your django website on localhost use the lxc containers IP address.
Find the lxc containers IP adress by running the following command when attached to the container:

.. code:: console

	$ ifconfig  

Use the IP address of the container when starting your django website. Access the website on http://%LXC-CONTAINER-IP%:%PORT%.

**Q: How can I access www-data crontab on a production machine?**

.. code:: console

	$ crontab -l -u www-data

**Q: How can I set up the datascanner-manager as a system service on the development machine**

Assuming You have put Your code in os2webscanner in your home directtory, You should copy the following file to
/etc/systemd/system/datascanner-manager.service after changing **YOU** in the following file to Your own username

.. code:: console

    [Unit]
    Description=Datascanner-manager service
    After=network.target

    [Service]
    Type=simple
    User=YOU
    WorkingDirectory=/home/YOU/os2webscanner
    ExecStart=/home/YOU/os2webscanner/python-env/bin/python  /home/YOU/os2webscanner/scrapy-webscanner/scanner_manager.py
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target

After that run

.. code:: console

    sudo systemctl enable datascanner-manager
    sudo systemctl start datascanner-manager

Be advised that You have to restart it whenever You make code changes to any of the modules it uses

**Q: I have started a filescan but nothing is being scanned on Ubuntu18.04 installation**

Starting a filescan causes the web server to mount the remote drive under the `/tmp/mnt/os2datascanner` folder. On Ubuntu 18.04, the `PrivateTmp` feature of systemd gives the web server its own `/tmp` folder that is not visible to the rest of the system, so the scan processes can't see the mount point.

As a temporary fix, `PrivateTmp` can be set to `false` so that the web server and the scan processes both share a common view of the `/tmp` folder.

Do the following:

.. code:: console

    cp /lib/systemd/system/apache2.service /etc/systemd/system/
    sed -i "s/PrivateTmp=true/PrivateTmp=false/g" /etc/systemd/system/apache2.service
    systemctl daemon-reload
    systemctl restart apache2.service

