"""
Juno

A clean pywebassembly wrapper which exposes host functions. Implements the EEI specified at
https://github.com/ewasm/design.

Lane Rettig <lanerettig@gmail.com>

Based on: https://gist.github.com/poemm/18ad5ef1e658c0ed195e271068839b84 by Paul Dworzanski
"""
import logging
import pywebassembly as wasm


def has_wasm_preamble(code):
    return len(code) >= 8 and code[0:8] == b'\x00asm\x01\x00\x00\x00'


def useGas(store,arg):
    # if VERBOSE>1: print("useGas(",arg,")")
    store["gasLeft"] -= arg[0]
    print("Taking gas ", arg[0], ", new gas left ", store["gasLeft"])
    if store["gasLeft"]<0:
        return store,"trap"
    else:
        return store,[]


def getGasLeft(store,arg):
    # if VERBOSE>1: print("getGasLeft(",arg,")")
    return store,store["gasLeft"]


"""
 The following EEI ("Ethereum Environment Interface") is implemented as a Wasm module.
 Each EEI function is allocated as a Wasm host func.
 Using Wasm conventions allows using Wasm semantics when contracts import and call these EEI functions.
"""


def instantiate_eei_module(store,modules,gas):
    # if VERBOSE>1: print("instantiate_eei_module()")
    store["gasLeft"] = gas	#modify store with a gasLeft field, this is not in the Wasm spec
    wasm.alloc_func(store, [["i64"],[]], useGas)
    wasm.alloc_func(store, [[],["i64"]], getGasLeft)
    modules["ethereum"] = {"types": [[["i64"], []],
                                     [[], ["i64"]],
                                     ],
                           "funcaddrs": [0, 1],
                           "tableaddrs": [],
                           "memaddrs": [],
                           "globaladdrs": [],
                           "exports": [{"name": "useGas", "value": ["func", 0]},
                                       {"name": "getGasLeft", "value": ["func", 1]},
                                       ]
                           }


"""
 The following function is used to call a given contract.
 This will "spin-up" a new VM, execute the contract, and output the contract's return values and gas used.
"""


# def call_contract(code, moduleid, args, gas):
def juno_execute(state, msg, tx_context, computation):
    logger = logging.getLogger('juno')

    code = computation.code
    gas = msg.gas
    args = msg.data

    if not has_wasm_preamble(code):
        raise Exception("Invalid code")

    logger.debug('juno_execute')
    # if VERBOSE>1: print("call_contract(",moduleid,funcname,arg,gas,")")
    # spin-up a VM instance with eei module
    modules = {}			#all moduleinst's indexed by their names, used to call funcs and resolve exports
    registered_modules = {}	#all moduleinst's which can be imported from, indexed by their registered name
    store = wasm.init_store()	#done once and lasts for lifetime of this abstract machine
    instantiate_eei_module(store,modules,gas)	#instantiate the EEI module "ethereum"
    registered_modules["ethereum"] = modules["ethereum"] 		#register module "ethereum" to be import-able
    # instantiate module which contains the func to-be-called
    # module_as_bytes = trinity.get_module_as_bytes(moduleid)	#TODO: need API to get module bytes
    module = wasm.decode_module(code)		#get module as abstract syntax
    externvalstar = []					#populate imports
    for import_ in module["imports"]:
        if import_["module"] not in registered_modules:
            logger.error('module not in registered_modules')
            return -1, -1
        importmoduleinst = registered_modules[import_["module"]]
        externval = None
        for export in importmoduleinst["exports"]:
            if export["name"] == import_["name"]:
                externval = export["value"]
        if externval == None:
            logger.error('Missing import')
            return None #error
        if externval[0] != import_["desc"][0]:
            logger.error('Bad imported function signature')
            return None #error
        externvalstar += [externval]
    store,moduleinst,ret = wasm.instantiate_module(store,module,externvalstar)
    # finally, call the function
    externval = wasm.get_export(moduleinst, "main")	#we want to call function "main"
    funcaddr = externval[1]				#the address of the funcname
    store,ret = wasm.invoke_func(store,funcaddr,args)	#finally, invoke the function
    print("Initial gas was ", gas, ", gas left is ", store["gasLeft"])
    computation.consume_gas(gas - store["gasLeft"], "juno")
    # return ret, gas - store["gasLeft"]
