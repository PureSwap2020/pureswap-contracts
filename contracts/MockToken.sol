// SPDX-License-Identifier: MIT

pragma solidity ^0.6.12;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {

    constructor(string memory name, string memory symbol, uint8 _decimal_) public ERC20(name, symbol) {
        _setupDecimals(_decimal_);
        _mint(msg.sender, 1000000000*10**uint(_decimal_));
    }

}