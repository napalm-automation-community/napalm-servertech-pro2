# napalm-servertech-pro2

Community NAPALM driver for PRO2 family [ServerTech](https://www.servertech.com/) PDUs running `8.0m` and higher (first version to implement the JSON API Web Service, a.k.a. JAWS).

## Supported features

Given the nature of those "network devices" is a bit particular, some functions cannot be implemented or will not make a lot of sense. First of all, the API only allows us to directly configure elements: it is not possible to confirm or rollback changes.

Please find below the list of supported getters:

* get_config
* get_environment
* get_facts
* get_interfaces (will return the `NET` interface management information and electrical outlets)
* get_interfaces_ip (will only return the `NET` interface management address)
* get_users

## Contributing
Please read [CONTRIBUTING](CONTRIBUTING) for details on our process for submitting issues and requests.

## License
This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details
