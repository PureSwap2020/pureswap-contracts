// SPDX-License-Identifier: GPL-3.0

pragma solidity =0.6.12;

import './interfaces/IUniswapV2Factory.sol';
import './PureSwapPair.sol';

contract PureSwapFactory is IUniswapV2Factory {
    address public feeToPure;
    address public feeToMx;
    address public override feeToSetter;
    address public override migrator;

    mapping(address => mapping(address => address)) public override getPair;
    address[] public override allPairs;

    event PairCreated(address indexed token0, address indexed token1, address pair, uint);

    constructor(address _feeToSetter) public {
        feeToSetter = _feeToSetter;
    }

    function allPairsLength() external override view returns (uint) {
        return allPairs.length;
    }

    function pairCodeHash() external pure returns (bytes32) {
        return keccak256(type(PureSwapPair).creationCode);
    }

    function createPair(address tokenA, address tokenB) external override returns (address pair) {
        require(tokenA != tokenB, 'PureSwap: IDENTICAL_ADDRESSES');
        (address token0, address token1) = tokenA < tokenB ? (tokenA, tokenB) : (tokenB, tokenA);
        require(token0 != address(0), 'PureSwap: ZERO_ADDRESS');
        require(getPair[token0][token1] == address(0), 'PureSwap: PAIR_EXISTS'); // single check is sufficient
        bytes memory bytecode = type(PureSwapPair).creationCode;
        bytes32 salt = keccak256(abi.encodePacked(token0, token1));
        assembly {
            pair := create2(0, add(bytecode, 32), mload(bytecode), salt)
        }
        PureSwapPair(pair).initialize(token0, token1);
        getPair[token0][token1] = pair;
        getPair[token1][token0] = pair; // populate mapping in the reverse direction
        allPairs.push(pair);
        emit PairCreated(token0, token1, pair, allPairs.length);
    }

    function feeTo() external view override returns(address _feeToPure, address _feeToMx) {
        _feeToPure = feeToPure;
        _feeToMx = feeToMx;
    }

    function setFeeTo(address _feeToPure, address _feeToMx) external override {
        require(msg.sender == feeToSetter, 'PureSwap: FORBIDDEN');
        feeToPure = _feeToPure;
        feeToMx = _feeToMx;
    }

    function setMigrator(address _migrator) external override {
        require(msg.sender == feeToSetter, 'PureSwap: FORBIDDEN');
        migrator = _migrator;
    }

    function setFeeToSetter(address _feeToSetter) external override {
        require(msg.sender == feeToSetter, 'PureSwap: FORBIDDEN');
        feeToSetter = _feeToSetter;
    }

}
