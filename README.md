# Ruff2BitBucket

[ruff](https://docs.astral.sh/ruff/) stands out as an exceptionally swift Python linter and code formatter, written in Rust. This tool not only expedites the process of identifying and correcting code issues but also demonstrates a powerful synergy between the efficiency of Rust and the versatility of Python, providing developers with a robust solution for enhancing code quality and adherence to coding standards.

[BitBucket](https://bitbucket.org/), an Atlassian product, serves as a comprehensive platform offering a visual Git interface, essentially presenting developers with an intuitive and user-friendly environment for managing their version-controlled code repositories.

Utilizing the ruff2bitbucket tool facilitates the seamless execution of your ruff validations, enabling you to effortlessly execute these checks and subsequently upload the results as a cohesive code insight directly into your BitBucket repository.

## Installation
```shell
pip install ruff2bitbucket
```

## Usage
Change your directory to where the configuration file is stored and run:
```shell
ruff2bitbucket [--user ...] [--pass ...]
```

⚠ It's important that you are in the right directory!

## Configuration
### ruff
For a comprehensive understanding of how to enhance and customize your code analysis, it is highly recommended to consult the [ruff configuration docs](https://docs.astral.sh/ruff/configuration/) and the [ruff settings docs](https://docs.astral.sh/ruff/settings/) where detailed instructions are provided on the modification of your pyproject.toml (or ruff.toml, or .ruff.toml) file, allowing you to tailor these configuration files to incorporate a broader range of checks and ensure a more thorough examination of your codebase.

### BitBucket
To begin configuring code insights, ensure that you have the necessary permissions in your Bitbucket repository.
- Navigate to your repository and click on "Settings" in the left sidebar.
- From the settings menu, select "Code insights" and then choose "Repository settings".
- Here, you can enable various code insights features.
- Add "ruff2bitbucket" as a code insight to enable this in your Pull Requests.

- By following these steps, you'll have the `ruff2bitbucket` code insight configured in Bitbucket, streamline the code review process. This integration fosters a more collaborative and efficient development environment, ultimately leading to higher-quality software.

## Security
When neither a username nor a password is explicitly provided (via the command line), the system will conduct a scan of environment variables for potential matches resembling `USER`/`USR` and `PASS`/`PW`.
Upon identifying a match, these discovered credentials will be employed to seamlessly attach annotations to the current commit hash, ensuring a streamlined process for handling authentication in the given environment.
This approach enhances flexibility while maintaining a focus on security, allowing users to conveniently utilize environment variables for authentication without compromising the integrity of the process.