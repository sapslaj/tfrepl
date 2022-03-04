# `tfrepl`

Terraform REPL

Very hacky and alpha. Sort of a preview of `terraform console` _could_ be.

## vs `terraform console`

- (customizable and themable) Syntax highlighting
- Input history
- Creates a full root module to evaluate code in, rather than only evaluating expressions
- Supports multiline editing and editing via `EDITOR`
- Syntax sugar shortcuts not available in vanilla HCL

## Examples

### Evaluate a function and get its output

```shell
$ tfrepl
Copying skeleton from /home/sapslaj/.tfrepl/skel
Starting REPL in /var/folders/kt/y6t6w70n1_j9q0d4d4q7q03w0000gn/T/tmpwbg4yypi
1 > = cidrsubnets("192.0.2.0/24", 2, 2)
2 ...
output "output" {
  value = cidrsubnets("192.0.2.0/24", 2, 2)
}


Initializing the backend...

Initializing provider plugins...

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.

Changes to Outputs:
  + output = [
      + "192.0.2.0/26",
      + "192.0.2.64/26",
    ]

You can apply this plan to save these new output values to the Terraform state, without changing any real infrastructure.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform apply" now.
1 >
```

### Getting output from data source

```shell
$ tfrepl
Copying skeleton from /home/sapslaj/.tfrepl/skel
1 > data "github_repository" "this" {
2 ... full_name = "sapslaj/tfrepl"
3 ... }
4 > = data.github_repository.this.branches
6 ...
data "github_repository" "this" {
  full_name = "sapslaj/tfrepl"
}
output "output" {
  value = data.github_repository.this.branches
}


Initializing the backend...

Initializing provider plugins...
- Finding latest version of hashicorp/github...
- Installing hashicorp/github v4.20.1...
- Installed hashicorp/github v4.20.1 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

╷
│ Warning: Additional provider information from registry
│
│ The remote registry returned warnings for registry.terraform.io/hashicorp/github:
│ - For users on Terraform 0.13 or greater, this provider has moved to integrations/github. Please update your source in required_providers.
╵

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.

Changes to Outputs:
  + output = [
      + {
          + name      = "main"
          + protected = false
        },
    ]

You can apply this plan to save these new output values to the Terraform state, without changing any real infrastructure.

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform apply" now.
1 >
```

You can add `.tf` files to `~/.tfrepl/skel` and it will copy that into the temp directory it creates. This is useful for defining default providers and such.
