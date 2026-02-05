from pydantic2ts import generate_typescript_defs

# to get this to work you need to istall a cli npm utility called json-schema-to-typescript

# on mac, run `npm install -g json-schema-to-typescript`

# if you get a permission issue (like unable to mkird /usr/local/lib/node_modules), you can run 
# `sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}`


# after that, you should get 


generate_typescript_defs("./addons/vsource.py", "../frontend/src/lib/addons/vsource/interface.ts")
generate_typescript_defs("./addons/vsense.py", "../frontend/src/lib/addons/vsense/interface.ts")