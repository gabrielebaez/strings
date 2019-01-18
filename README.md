# Strings

The goal is to develop an easy to use, ledger database system based on [sophia](http://sophia.systems)

#### why?
For kicks and giggles of course.

#### Installation

```
pip install virtualenv
pip install -r requirements_devel
```

#### How to run

Create a .env file from env_example and fill in the data

```
source venv/bin/activate
python main.py
```

#### Roadmap

- [x] Basic definition of structure and simple ledger validation.
- [ ] Storage engine for persistence.
- [ ] Implementation of consensus.
- [ ] Query capabilities.
- [ ] Deployment/management tooling.