---
title: "License"
schema_type: common
status: published
owner: core-maintainer
purpose: "License information for {{ cookiecutter.project_name }}."
tags:
  - project
  - license
---

{{ cookiecutter.project_name }} is licensed under the **{{ cookiecutter.license }}** License.

## Summary

{% if cookiecutter.license == "MIT" -%}
The MIT License is a permissive license that allows:

- **Commercial use**: Use in commercial projects
- **Modification**: Modify the source code
- **Distribution**: Distribute copies
- **Private use**: Use privately

With the following conditions:

- **License and copyright notice**: Include the license in distributions
{% elif cookiecutter.license == "Apache-2.0" -%}
The Apache 2.0 License allows:

- **Commercial use**: Use in commercial projects
- **Modification**: Modify the source code
- **Distribution**: Distribute copies
- **Patent use**: Use patent claims
- **Private use**: Use privately

With the following conditions:

- **License and copyright notice**: Include the license
- **State changes**: Document changes to the code
{% else -%}
See the LICENSE file for full terms.
{% endif -%}

## Full License Text

See the [LICENSE]({{ cookiecutter.repo_url }}/blob/main/LICENSE) file in the repository root.

## Third-Party Licenses

This project uses open-source dependencies. See `pyproject.toml` for the full list.

## Contact

For licensing questions, contact: {{ cookiecutter.author_email }}
