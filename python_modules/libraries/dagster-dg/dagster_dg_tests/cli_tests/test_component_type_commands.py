import textwrap
from pathlib import Path

import pytest
from dagster_dg.context import CodeLocationDirectoryContext, DgContext
from dagster_dg.utils import ensure_dagster_dg_tests_import

ensure_dagster_dg_tests_import()

from dagster_dg_tests.utils import (
    ProxyRunner,
    assert_runner_result,
    isolated_example_code_location_bar,
    isolated_example_deployment_foo,
    modify_pyproject_toml,
)

# ########################
# ##### GENERATE
# ########################


@pytest.mark.parametrize("in_deployment", [True, False])
def test_component_type_generate_success(in_deployment: bool) -> None:
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner, in_deployment):
        result = runner.invoke("component-type", "generate", "baz")
        assert_runner_result(result)
        assert Path("bar/lib/baz.py").exists()
        context = CodeLocationDirectoryContext.from_path(Path.cwd(), DgContext.default())
        assert context.has_component_type("bar.baz")


def test_component_type_generate_outside_code_location_fails() -> None:
    with ProxyRunner.test() as runner, isolated_example_deployment_foo(runner):
        result = runner.invoke("component-type", "generate", "baz")
        assert_runner_result(result, exit_0=False)
        assert "must be run inside a Dagster code location directory" in result.output


@pytest.mark.parametrize("in_deployment", [True, False])
def test_component_type_generate_already_exists_fails(in_deployment: bool) -> None:
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner, in_deployment):
        result = runner.invoke("component-type", "generate", "baz")
        assert_runner_result(result)
        result = runner.invoke("component-type", "generate", "baz")
        assert_runner_result(result, exit_0=False)
        assert "already exists" in result.output


def test_component_type_generate_succeeds_non_default_component_lib_package() -> None:
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        alt_lib_path = Path("bar/_lib")
        alt_lib_path.mkdir(parents=True)
        with modify_pyproject_toml() as pyproject_toml:
            pyproject_toml["tool"]["dg"]["components_lib_package"] = "bar._lib"
            pyproject_toml["project"]["entry-points"]["dagster.components"]["bar"] = "bar._lib"
        result = runner.invoke(
            "component-type",
            "generate",
            "baz",
        )
        assert_runner_result(result)
        assert Path("bar/_lib/baz.py").exists()
        context = CodeLocationDirectoryContext.from_path(Path.cwd(), DgContext.default())
        assert context.has_component_type("bar.baz")


def test_component_type_generate_fails_components_lib_package_does_not_exist() -> None:
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        with modify_pyproject_toml() as pyproject_toml:
            pyproject_toml["tool"]["dg"]["components_lib_package"] = "bar._lib"
            pyproject_toml["project"]["entry-points"]["dagster.components"]["bar"] = "bar._lib"
        result = runner.invoke(
            "component-type",
            "generate",
            "baz",
        )
        assert_runner_result(result, exit_0=False)
        assert "Components lib package `bar._lib` is not installed" in str(result.exception)


# ########################
# ##### INFO
# ########################


def test_component_type_info_all_metadata_success():
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.simple_pipes_script_asset",
        )
        assert_runner_result(result)
        assert (
            result.output.strip()
            == textwrap.dedent("""
            dagster_components.test.simple_pipes_script_asset

            Description:

            A simple asset that runs a Python script with the Pipes subprocess client.

            Because it is a pipes asset, no value is returned.

            Generate params schema:

            {
                "properties": {
                    "asset_key": {
                        "title": "Asset Key",
                        "type": "string"
                    },
                    "filename": {
                        "title": "Filename",
                        "type": "string"
                    }
                },
                "required": [
                    "asset_key",
                    "filename"
                ],
                "title": "SimplePipesScriptAssetParams",
                "type": "object"
            }

            Component params schema:

            {
                "properties": {
                    "asset_key": {
                        "title": "Asset Key",
                        "type": "string"
                    },
                    "filename": {
                        "title": "Filename",
                        "type": "string"
                    }
                },
                "required": [
                    "asset_key",
                    "filename"
                ],
                "title": "SimplePipesScriptAssetParams",
                "type": "object"
            }
        """).strip()
        )


def test_component_type_info_all_metadata_empty_success():
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.all_metadata_empty_asset",
        )
        assert_runner_result(result)
        assert (
            result.output.strip()
            == textwrap.dedent("""
                dagster_components.test.all_metadata_empty_asset
            """).strip()
        )


def test_component_type_info_flag_fields_success():
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.simple_pipes_script_asset",
            "--description",
        )
        assert_runner_result(result)
        assert (
            result.output.strip()
            == textwrap.dedent("""
            A simple asset that runs a Python script with the Pipes subprocess client.

            Because it is a pipes asset, no value is returned.
        """).strip()
        )

        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.simple_pipes_script_asset",
            "--generate-params-schema",
        )
        assert_runner_result(result)
        assert (
            result.output.strip()
            == textwrap.dedent("""
                {
                    "properties": {
                        "asset_key": {
                            "title": "Asset Key",
                            "type": "string"
                        },
                        "filename": {
                            "title": "Filename",
                            "type": "string"
                        }
                    },
                    "required": [
                        "asset_key",
                        "filename"
                    ],
                    "title": "SimplePipesScriptAssetParams",
                    "type": "object"
                }
            """).strip()
        )

        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.simple_pipes_script_asset",
            "--component-params-schema",
        )
        assert_runner_result(result)
        assert (
            result.output.strip()
            == textwrap.dedent("""
                {
                    "properties": {
                        "asset_key": {
                            "title": "Asset Key",
                            "type": "string"
                        },
                        "filename": {
                            "title": "Filename",
                            "type": "string"
                        }
                    },
                    "required": [
                        "asset_key",
                        "filename"
                    ],
                    "title": "SimplePipesScriptAssetParams",
                    "type": "object"
                }
            """).strip()
        )


def test_component_type_info_outside_code_location_fails() -> None:
    with ProxyRunner.test() as runner, runner.isolated_filesystem():
        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.simple_pipes_script_asset",
            "--component-params-schema",
        )
        assert_runner_result(result, exit_0=False)
        assert "must be run inside a Dagster code location directory" in result.output


def test_component_type_info_multiple_flags_fails() -> None:
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        result = runner.invoke(
            "component-type",
            "info",
            "dagster_components.test.simple_pipes_script_asset",
            "--description",
            "--generate-params-schema",
        )
        assert_runner_result(result, exit_0=False)
        assert (
            "Only one of --description, --generate-params-schema, and --component-params-schema can be specified."
            in result.output
        )


# ########################
# ##### LIST
# ########################


def test_list_component_types_success():
    with ProxyRunner.test() as runner, isolated_example_code_location_bar(runner):
        result = runner.invoke("component-type", "list")
        assert_runner_result(result)
        assert (
            result.output.strip()
            == textwrap.dedent("""
            dagster_components.test.all_metadata_empty_asset
            dagster_components.test.simple_asset
                A simple asset that returns a constant string value.
            dagster_components.test.simple_pipes_script_asset
                A simple asset that runs a Python script with the Pipes subprocess client.
        """).strip()
        )


def test_list_component_types_outside_code_location_fails() -> None:
    with ProxyRunner.test() as runner, runner.isolated_filesystem():
        result = runner.invoke("component-type", "list")
        assert_runner_result(result, exit_0=False)
        assert "must be run inside a Dagster code location directory" in result.output
