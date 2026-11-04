"""Typing contract: every public REST method is annotated and py.typed ships."""

import importlib
import inspect
import pathlib

import okx

OKX_ROOT = pathlib.Path(okx.__file__).parent
API_MODULES = [
    "okx.Account",
    "okx.Affiliate",
    "okx.BlockTrading",
    "okx.Convert",
    "okx.CopyTrading",
    "okx.DualInvest",
    "okx.FDBroker",
    "okx.Funding",
    "okx.Grid",
    "okx.MarketData",
    "okx.PublicData",
    "okx.SpreadTrading",
    "okx.Status",
    "okx.SubAccount",
    "okx.Trade",
    "okx.TradingData",
    "okx.Finance.EthStaking",
    "okx.Finance.FlexibleLoan",
    "okx.Finance.Okusd",
    "okx.Finance.Savings",
    "okx.Finance.SolStaking",
    "okx.Finance.StakingDefi",
]


def _public_methods():
    for module_name in API_MODULES:
        module = importlib.import_module(module_name)
        for class_name, cls in vars(module).items():
            if not inspect.isclass(cls) or not class_name.endswith("API"):
                continue
            if cls.__module__ != module.__name__:
                continue
            for method_name, method in vars(cls).items():
                if method_name.startswith("_") or not inspect.isfunction(method):
                    continue
                yield cls, method_name, method


def test_every_public_method_has_a_return_annotation():
    missing = [
        f"{cls.__name__}.{name}"
        for cls, name, method in _public_methods()
        if inspect.signature(method).return_annotation is inspect.Signature.empty
    ]
    assert missing == []


def test_every_public_method_annotates_its_parameters():
    missing = []
    for cls, name, method in _public_methods():
        for parameter in inspect.signature(method).parameters.values():
            if parameter.name == "self":
                continue
            if parameter.annotation is inspect.Signature.empty:
                missing.append(f"{cls.__name__}.{name}({parameter.name})")
    assert missing == []


def test_py_typed_marker_exists():
    assert (OKX_ROOT / "py.typed").is_file()
