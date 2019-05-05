# Cookiecutter template for Rust full stack web application

This template provides a full stack rust application, using `rocket` in the backend and `seed` in the frontend.
The project is split into 3 subprojects:

 * `backend` - Implements the server side using the `rocket` web framework.
 * `frontend` - Implments the frontend using `seed`, `bootstrap` and `scss`, packaged together using `webpack`.
 * `shared` - Is a dependency of both `backend` and `frontend` and allows sharing code between them. Specifically it is useful to share structs which are serialized using `serde`.


## Installing

We include a small build tool called [wasp](https://github.com/raffber/wasp). From your package manager make sure you have `rustup` and `npm` installed.

```
$ rustup update
$ rustup target add wasm32-unknown-unknown
$ ./wasp setup
```


## Building

Simply run:

```
$ ./wasp build
```

This will build backend, frontend and package everything together with webpack. It can then be used either using:


```
$ ./wasp run 
```

Or just by running

```
$ cd backend
$ cargo run
```

The build tool also provides an automatic rebuild in case files were changed on the drive. It will automatically rebuild the `frontend` and `backend` projects as required and restart the webserver. Run it with:

```
$ ./wasp watch
```

Note that this depends upon having `pyinotify` installed and running linux.


## Deploying

It is possible to create prebuilt zip-package for deployment with all files relevant files included using:

```
$ ./wasp release
```

The compiled package will be ready in `build/prod.zip`.

There are deployment files ready in the `deploy` folder.
We make use of `nginx` to serve static files and as reverse proxy to invoke `backend`.

The `deploy.sh` shell script gives a reference of all the required steps to deploy the app.




