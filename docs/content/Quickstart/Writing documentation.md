#### Clone the repo
Working on the firmware, software, or documentation for the device bay system starts with cloning the repository. 

```shell
git clone https://github.com/bkorzh/dbay.git
```


The documentation is located in the [`docs`](https://github.com/bkorzh/dbay/tree/main/docs) folder in the root of the repository. Inside is a `content` folder, and a configuration file `quartz.config.ts`. The content folder contains the documentation files themselves, and the config file specifies features of the built quartz website like colors, fonts, other styling. 

#### Write docs with Obsidian

Open obsidian, and open the `/docs/content` folder as an obsidian vault. There is already a config folder `.obsidian` inside `/docs/content`. The vault is set up to store attachments like images inside the `/docs/content/attachments` folder, so you should make sure that you're obsidian editor is set to use this `attachments` folder. In the bottom left-hand corner, select the gear icon and open `Files and links`. Under `Default location for new attachments`, make sure the drop down menu is set to `In the folder specified below`. Set the `Attachment folder path` item below to `attachments`. 

![[set_to_attachments.png]]

